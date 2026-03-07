"""邮件子智能体"""

import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph

from src.agents.multi_task_agent.state import MultiTaskState
from src.agents.multi_task_agent.tools import validate_email_address, send_email


# 邮件智能体的系统提示词
MAIL_AGENT_SYSTEM_PROMPT = """你是一个邮件助手，负责帮助用户发送邮件。

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - mail_address: 收件人邮箱地址
   - mail_topic: 邮件主题
   - mail_content: 邮件内容

2. **校验信息**：
   - 使用 validate_email_address 工具验证邮箱地址格式
   - 确保所有必填字段都已填写

3. **展示信息并请求确认**：
   在执行发送前，向用户展示以下信息：
   ```
   准备发送邮件：
   - 收件人：{mail_address}
   - 主题：{mail_topic}
   - 内容：{mail_content}

   请确认是否发送（回复 yes 或 no）：
   ```

4. **执行发送**：
   - 只有在用户明确回复 "yes" 后，才调用 send_email 工具
   - 如果用户回复 "no"，询问是否需要修改

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- 在信息收集完成后，先进行校验
- 校验通过后，展示信息并请求用户确认
- 只有用户明确同意后，才执行发送操作
"""


async def mail_agent_node(state: MultiTaskState) -> MultiTaskState:
    """邮件智能体节点"""
    from src.agents.common import load_chat_model
    from src import config as sys_config

    # 获取模型
    model = load_chat_model(sys_config.default_model)

    # 绑定工具
    tools = [validate_email_address, send_email]
    model_with_tools = model.bind_tools(tools)

    # 获取最新的消息
    messages = state.messages

    # 调用模型
    response = await model_with_tools.ainvoke(
        [
            {"role": "system", "content": MAIL_AGENT_SYSTEM_PROMPT},
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
    if "请确认是否发送" in response.content or "回复 yes 或 no" in response.content:
        state.awaiting_user_confirmation = True
        state.collected_info.update({
            "mail_address": state.collected_info.get("mail_address", ""),
            "mail_topic": state.collected_info.get("mail_topic", ""),
            "mail_content": state.collected_info.get("mail_content", ""),
        })

    return state


def create_mail_agent_node():
    """创建邮件智能体节点"""
    return mail_agent_node
