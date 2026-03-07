"""天气查询子智能体"""

from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph

from src.agents.multi_task_agent.state import MultiTaskState
from src.agents.multi_task_agent.tools import query_weather


# 天气查询智能体的系统提示词
WEATHER_AGENT_SYSTEM_PROMPT = """你是一个天气查询助手，负责帮助用户查询天气。

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - city: 城市名（必需）

2. **执行查询**：
   - 信息收集完成后，直接调用 query_weather 工具查询天气
   - 不需要用户确认

## 重要提示：

- 天气查询是一个简单的查询操作，不需要用户确认
- 保持对话友好和自然
- 信息收集完成后立即执行查询
"""


async def weather_agent_node(state: MultiTaskState) -> MultiTaskState:
    """天气查询智能体节点"""
    from src.agents.common import load_chat_model
    from src import config as sys_config

    # 获取模型
    model = load_chat_model(sys_config.default_model)

    # 绑定工具
    tools = [query_weather]
    model_with_tools = model.bind_tools(tools)

    # 获取最新的消息
    messages = state.messages

    # 调用模型
    response = await model_with_tools.ainvoke(
        [
            {"role": "system", "content": WEATHER_AGENT_SYSTEM_PROMPT},
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
                # 保存查询结果
                state.task_result = str(tool_result)

    return state


def create_weather_agent_node():
    """创建天气查询智能体节点"""
    return weather_agent_node
