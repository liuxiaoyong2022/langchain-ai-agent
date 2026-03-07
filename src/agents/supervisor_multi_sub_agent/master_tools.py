import os
import uuid
from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import InjectedToolCallId, tool
import re
import json
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from src.agents.common import BaseAgent, load_chat_model
from src import config
# 定义任务类型
class TaskType(BaseModel):
    """任务类型枚举"""
    EMAIL: str = Field(description="邮件任务",default="email")
    IMAGE_GEN: str = Field(description="图片生成任务",default="image_gen")
    TTS: str = Field(description="文字到语音转换任务",default="tts")
    MULTI: str = Field(description="多个子智能体协作任务",default="multi")  # 需要多个子智能体协作
    UNKNOWN: str = Field(description="未知任务",default="unknown")


class TaskPlan(BaseModel):
    """任务计划模型"""
    task_id: str = Field(description="任务唯一ID")
    task_type: str = Field(description="任务类型 取值范围为TaskType包括:'email','image_gen','tts','multi','unknown' ")
    overall_task: str = Field(description="任务描述")
    subtasks: List[Dict[str, Any]] = Field(default_factory=[], description="子任务列表")
    execution_order: str = Field(description="执行顺序：serial或parallel")
    requires_user_input: bool = Field(default=False, description="是否需要用户输入")
    dependencies:List[Dict[str, Any]]  = Field(default_factory={}, description="依赖的任务ID")
    # dependencies: dict[str:any] = Field(default_factory={}, description="依赖的任务ID")
    # dependencies: List[str] = Field(default_factory=[], description="依赖的任务ID")

@tool
def analyze_user_input( user_input: str) -> Dict[str, Any]:
    """
    分析用户输入，识别意图

    Args:
        user_input: 用户输入的文本

    Returns:
        分析结果，包含意图、实体、任务类型等
    """
    system_prompt = """你是一个任务分析专家。请分析用户输入，识别：

1. 用户意图（用户想做什么）
2. 涉及的任务类型（邮件处理、图片生成、语音合成等）
3. 关键实体（收件人、主题、参数等）
4. 任务复杂度（简单单任务 vs 复杂多任务）
5. 是否需要多步骤执行
6. 是否需要额外收集用户信息 

请以JSON格式返回分析结果,但不以json开头,直接返回json字符串。"""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"用户输入：{user_input}")
        ]
        print(f"step 0.5----------->开始进行用户输入分析 user_input:{user_input}")
        model = load_chat_model(config.default_model)
        # model = load_chat_model(context.model)
        response = model.invoke(messages)
        print(f"step 0.6----------->用户输入分析结果 response:{response.content}")
        # 尝试解析JSON响应
        try:
            analysis = json.loads(response.content)
            print(f"step 0.7----------->用户输入分析结果 analysis:{analysis}")
        except json.JSONDecodeError:
            # 如果LLM没有返回有效的JSON，使用规则分析
            print(f"step 0.8----------->JSONDecodeError analysis:{analysis}")
            # analysis = self._rule_based_analysis(user_input)

        return analysis

    except Exception as e:
        print(f"分析出错: {e}")
        # return _rule_based_analysis(user_input)



@tool
def create_task_plan( user_input: str, analysis: Dict[str, Any]) -> TaskPlan:
    """
    创建任务执行计划

    Args:
        user_input: 用户输入
        analysis: 分析结果

    Returns:
        任务计划
    """
    # task_id = f"task_{len(self.task_history) + 1}"
    print(f"step 0.8.1------>  create_task_plan   user_input:{user_input}   analysis:{analysis} ")

    # 使用LLM生成详细计划
    system_prompt = """你是一个任务规划专家。请根据用户意图和分析结果，创建详细的任务执行计划。

计划应包括：
1. 任务分解（将复杂任务分解为子任务）
2. 执行顺序（哪些任务可以并行，哪些必须串行）
3. 任务间的依赖关系可以用depends_on表示
4. 是否需要中断等待用户输入
5. 对于邮件处理不需要收集邮件服务器配置或授权信息
6. 每个子subtask用requires_user_input(bool类型)表示是否需要收集缺失信息 以及requires_items=[]表示具体缺失的字段
返回的task_plan应包括以下字段
    task_id: 描述:"任务唯一ID",字段类型:string
    task_type: 描述: "任务类型 取值范围仅限于:'email','image_gen','tts','multi','unknown'" ,字段类型:string
    overall_task: 描述:"任务描述",字段类型:string
    subtasks: 描述:"子任务列表,每个子任务要包括（
      1.subtask_id,
      2.description,
      3.task_type 
      4.agent_name:执行该子任务的agent名称(比如  mail_sub_agent, image_sub_agent, tts_sub_agent,))",字段类型:List列表
    execution_order: 描述: "执行顺序：serial或parallel" 字段类型:string
    requires_user_input: 描述: "是否需要用户输入" 字段类型:bool
    dependencies: 描述: "依赖的任务ID" 以列表list的数据结构返回 字段类型:List[Dict[str, Any]]列表

请以JSON格式返回task_plan任务计划,但不要包含'json'关键字。"""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=json.dumps({
                "user_input": user_input,
                "analysis": analysis
            }, ensure_ascii=False))
        ]
        model = load_chat_model(config.default_model)
        response = model.invoke(messages)
        plan_content = response.content
        print(f"step 0.8.1.1------>  plan_content:{plan_content}   ")

        # 尝试提取JSON
        if "```json" in plan_content:
            print(f"step 0.8.1.2------>  do remove :{"```json"}   ")
            plan_content = plan_content.split("```json")[1].split("```")[0].strip()
        elif "```" in plan_content:
            print(f"step 0.8.1.3------>  do remove :{"```"}   ")
            plan_content = plan_content.split("```")[1].split("```")[0].strip()

        # if plan_content.startswith("```json"):
        #     print(f"step 0.8.1.2------>  do replace:{"```json"}   ")
        #     plan_content = re.sub(f"^{re.escape('```json')}", "```", plan_content)

        print(f"step 0.8.2------>  create_task_plan   plan_content:{plan_content}   ")

        try:
            plan_data = json.loads(plan_content)
            if "task_plan" in plan_data:
                json_task_plan = plan_data["task_plan"]
            else:
                json_task_plan = plan_data

            # json_task_plan = plan_data
            # json_task_plan = plan_data["task_plan"]
            # json_task_plan["task_id"] = task_id
        except json.JSONDecodeError:
            print(f"step 0.8.4------> get JSONDecodeError to get json_task_plan ")
            # plan_data = self._create_fallback_plan(user_input, analysis, task_id)

    except Exception as e:
        print(f"计划生成出错: {e}")
        # plan_data = self._create_fallback_plan(user_input, analysis, task_id)

    # 创建TaskPlan对象
    print(f"step 0.8.3------>  create_task_plan  **plan_data:{json_task_plan}   ")
    task_plan = TaskPlan(**json_task_plan)
    # self.task_history.append(task_plan)
    # self.active_tasks[task_id] = task_plan

    return task_plan
