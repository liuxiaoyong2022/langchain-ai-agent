"""图片生成子智能体"""

import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph

from src.agents.multi_task_agent.state import MultiTaskState
from src.agents.multi_task_agent.tools import validate_image_params, generate_image


# 图片生成智能体的系统提示词
IMAGE_AGENT_SYSTEM_PROMPT = """你是一个图片生成助手，负责帮助用户生成图片。

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - description: 图片描述（必需）
   - style: 图片风格，如 "写实"、"印象"、"卡通" 等（必需）
   - width: 图片宽度，像素单位，如 1024（必需）
   - height: 图片高度，像素单位，如 768（必需）
   - count: 图片数量，1-10 张（必需）

2. **校验信息**：
   - 使用 validate_image_params 工具验证所有参数
   - 确保所有必填字段都已填写
   - 确保参数值在合理范围内

3. **展示信息并请求确认**：
   在执行生成前，向用户展示以下信息：
   ```
   准备生成图片：
   - 描述：{description}
   - 风格：{style}
   - 尺寸：{width}x{height}
   - 数量：{count} 张

   请确认是否生成（回复 yes 或 no）：
   ```

4. **执行生成**：
   - 只有在用户明确回复 "yes" 后，才调用 generate_image 工具
   - 如果用户回复 "no"，询问是否需要修改

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- 在信息收集完成后，先进行校验
- 校验通过后，展示信息并请求用户确认
- 只有用户明确同意后，才执行生成操作
"""


async def image_agent_node(state: MultiTaskState) -> MultiTaskState:
    """图片生成智能体节点"""
    from src.agents.common import load_chat_model
    from src import config as sys_config

    # 获取模型
    model = load_chat_model(sys_config.default_model)

    # 绑定工具
    tools = [validate_image_params, generate_image]
    model_with_tools = model.bind_tools(tools)

    # 获取最新的消息
    messages = state.messages

    # 调用模型
    response = await model_with_tools.ainvoke(
        [
            {"role": "system", "content": IMAGE_AGENT_SYSTEM_PROMPT},
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
                if tool_call["name"] == "validate_image_params":
                    args = tool_call["args"]
                    state.collected_info.update(args)

    return state


def create_image_agent_node():
    """创建图片生成智能体节点"""
    return image_agent_node
