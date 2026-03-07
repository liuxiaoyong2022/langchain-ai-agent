"""TTS 子智能体"""

import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph

from src.agents.multi_task_agent.state import MultiTaskState
from src.agents.multi_task_agent.tools import validate_tts_params, generate_tts


# TTS 智能体的系统提示词
TTS_AGENT_SYSTEM_PROMPT = """你是一个 TTS（文本转语音）助手，负责帮助用户生成语音。

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - tts_content: 语音文案（必需）
   - voice_sample_url: 语音样本文件URL（可选，不提供则使用默认语音）

2. **校验信息**：
   - 使用 validate_tts_params 工具验证参数
   - 确保 tts_content 已填写

3. **展示信息并请求确认**：
   在执行生成前，向用户展示以下信息：
   ```
   准备生成 TTS 语音：
   - 文案：{tts_content}
   - 语音：{voice_sample_url or "使用默认语音"}

   请确认是否生成（回复 yes 或 no）：
   ```

4. **执行生成**：
   - 只有在用户明确回复 "yes" 后，才调用 generate_tts 工具
   - 如果用户回复 "no"，询问是否需要修改

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- voice_sample_url 是可选的，如果用户不提供，使用默认语音
- 在信息收集完成后，先进行校验
- 校验通过后，展示信息并请求用户确认
- 只有用户明确同意后，才执行生成操作
"""


async def tts_agent_node(state: MultiTaskState) -> MultiTaskState:
    """TTS 智能体节点"""
    from src.agents.common import load_chat_model
    from src import config as sys_config

    # 获取模型
    model = load_chat_model(sys_config.default_model)

    # 绑定工具
    tools = [validate_tts_params, generate_tts]
    model_with_tools = model.bind_tools(tools)

    # 获取最新的消息
    messages = state.messages

    # 调用模型
    response = await model_with_tools.ainvoke(
        [
            {"role": "system", "content": TTS_AGENT_SYSTEM_PROMPT},
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
    if "请确认是否生成" in response.content or "回复 yes 或 no" in response.content:
        state.awaiting_user_confirmation = True
        # 更新收集的信息
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "validate_tts_params":
                    args = tool_call["args"]
                    state.collected_info.update(args)

    return state


def create_tts_agent_node():
    """创建 TTS 智能体节点"""
    return tts_agent_node
