"""数字人子智能体"""

import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph

from src.agents.multi_task_agent.state import MultiTaskState
from src.agents.multi_task_agent.tools import validate_digital_human_params, create_digital_human


# 数字人智能体的系统提示词
DIGITAL_HUMAN_AGENT_SYSTEM_PROMPT = """你是一个数字人制作助手，负责帮助用户制作数字人视频。

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - digital_image: 数字人图片（必需）
   - digital_content: 数字人口播文稿（必需）
   - digital_sample: 数字人口播声音样本URL（可选，不提供则使用默认声音）

2. **校验信息**：
   - 使用 validate_digital_human_params 工具验证参数
   - 确保所有必填字段都已填写

3. **展示信息并请求确认**：
   在执行制作前，向用户展示以下信息：
   ```
   准备制作数字人视频：
   - 数字人图片：{digital_image}
   - 口播文稿：{digital_content}
   - 声音样本：{digital_sample or "使用默认声音"}

   请确认是否制作（回复 yes 或 no）：
   ```

4. **执行制作**：
   - 只有在用户明确回复 "yes" 后，才调用 create_digital_human 工具
   - 如果用户回复 "no"，询问是否需要修改

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- digital_sample 是可选的，如果用户不提供，使用默认声音
- 在信息收集完成后，先进行校验
- 校验通过后，展示信息并请求用户确认
- 只有用户明确同意后，才执行制作操作
"""


async def digital_human_agent_node(state: MultiTaskState) -> MultiTaskState:
    """数字人智能体节点"""
    from src.agents.common import load_chat_model
    from src import config as sys_config

    # 获取模型
    model = load_chat_model(sys_config.default_model)

    # 绑定工具
    tools = [validate_digital_human_params, create_digital_human]
    model_with_tools = model.bind_tools(tools)

    # 获取最新的消息
    messages = state.messages

    # 调用模型
    response = await model_with_tools.ainvoke(
        [
            {"role": "system", "content": DIGITAL_HUMAN_AGENT_SYSTEM_PROMPT},
            *messages,
        ]
    )

    # 更新状态
    state.messages.append(response)

    # 如果有工具调用，处理工具调用
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            tool = {t.name: t for t in tools}.get(tool_call["name"])
            if tool:
                tool_result = tool.invoke(tool_call["args"])
                tool_message = ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
                state.messages.append(tool_message)

    # 检查是否需要用户确认
    if "请确认是否制作" in response.content or "回复 yes 或 no" in response.content:
        state.awaiting_user_confirmation = True
        # 更新收集的信息
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "validate_digital_human_params":
                    args = tool_call["args"]
                    state.collected_info.update(args)

    return state


def create_digital_human_agent_node():
    """创建数字人智能体节点"""
    return digital_human_agent_node
