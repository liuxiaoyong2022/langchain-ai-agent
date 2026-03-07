"""Master-Sub Agent Graph - 主控+子智能体图构建

基于 deep_agent 架构，使用 SubAgentMiddleware 实现主控智能体和多个子智能体协作
"""

from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from deepagents.middleware.subagents import SubAgentMiddleware
from langgraph.graph.state import CompiledStateGraph

from src.agents.common import BaseAgent, load_chat_model
from src.agents.common.backends import create_agent_composite_backend
from src.agents.common.middlewares import (
    RuntimeConfigMiddleware,
    save_attachments_to_fs,
)
from langchain.agents.middleware import TodoListMiddleware
from src.services.mcp_service import get_tools_from_all_servers
from src.utils import logger


from .context import MasterSubContext
from .tools import (
    get_master_sub_tools,
    get_mail_agent_tools,
    get_image_agent_tools,
    get_tts_agent_tools,
    get_weather_agent_tools,
    get_digital_human_agent_tools,
)


def _create_fs_backend(rt):
    """创建文件存储后端"""
    return create_agent_composite_backend(rt)


# ==================== 子智能体定义 ====================

def _get_mail_sub_agent(tools: list) -> dict:
    """邮件子智能体"""
    return {
        "name": "mail-agent",
        "description": "邮件助手，负责发送邮件",
        "system_prompt": """你是一个邮件助手，负责帮助用户发送邮件。


## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - mail_address: 收件人邮箱地址
   - mail_topic: 邮件主题
   - mail_content: 邮件内容

2. **校验信息**：
   - 使用 validate_email_address 工具验证邮箱地址格式
   - 确保所有必填字段都已填写

3. **展示信息并请求确认**：
   校验通过后，向用户展示以下信息：
   ```
   准备发送邮件：
   - 收件人：{mail_address}
   - 主题：{mail_topic}
   - 内容：{mail_content}

   请确认是否发送（请回复 yes 或 no）：
   ```

4. **等待用户明确确认**：
   - ⚠️ 必须停止，等待用户回复
   - 只有收到：yes、是、好的、确认、同意、可以，才能继续
   - 如果收到：no、不、不要、取消，则询问是否需要修改
   - ⚠️ 在收到用户明确确认前，绝对不能调用 send_email 工具

5. **执行发送**：
   - 只有在用户明确确认后，才调用 send_email 工具

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- ⚠️ 必须等待用户明确确认（yes/是/好的/确认/同意）才能调用 send_email
""",
        "tools": tools,
    }


def _get_image_sub_agent(tools: list) -> dict:
    """图片生成子智能体"""
    return {
        "name": "image-agent",
        "description": "图片生成助手，负责生成图片",
        "system_prompt": """你是一个图片生成助手，负责帮助用户生成图片。


你必须严格遵守以下流程，任何时候都不能跳过或省略：

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息（每次只询问一个）：
   - description: 图片描述（必需）
   - style: 图片风格，如 "写实"、"印象"、"卡通" 等（必需）
   - width: 图片宽度，像素单位，如 1024（必需）
   - height: 图片高度，像素单位，如 768（必需）
   - count: 图片数量，1-10 张（必需）

2. **校验信息**：
   - 使用 validate_image_params 工具验证所有参数
   - 确保所有必填字段都已填写
   - 确保参数值在合理范围内

3. **展示信息并请求确认**（必须步骤）：
   校验通过后，向用户展示以下信息并明确请求确认：
   ```
   准备生成图片：
   - 描述：{description}
   - 风格：{style}
   - 尺寸：{width}x{height}
   - 数量：{count} 张

   请确认是否生成（请回复 yes 或 no）：
   ```

4. **等待用户明确确认**：
   - ⚠️ 在此步骤必须停止，等待用户回复
   - 只有收到以下明确肯定回复后才能继续：yes、是、好的、确认、同意、可以
   - 如果收到：no、不、不要、取消，则询问是否需要修改
   - ⚠️ 在收到用户明确确认前，绝对不能调用 generate_image 工具

5. **执行生成**：
   - 只有在用户明确回复 "yes" 等肯定词后，才调用 generate_image 工具

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- 在信息收集完成后，先进行校验
- 校验通过后，展示信息并请求用户确认
- ⚠️ 最重要：必须等待用户明确确认（yes/是/好的/确认/同意）才能调用 generate_image
- 如果用户没有明确确认，继续等待，不要执行任何工具调用

## 对话示例：

用户：帮我生成一张图片
你：好的，我可以帮您生成图片。请问图片的描述是什么？
用户：一只可爱的橘猫
你：您希望使用什么风格？比如写实、印象、卡通等。
用户：写实风格
你：图片尺寸是多少？比如 1024x768
用户：1024x768
你：需要生成几张图片？（1-10张）
用户：1张
你：[调用 validate_image_params 校验参数]

准备生成图片：
- 描述：一只可爱的橘猫
- 风格：写实
- 尺寸：1024x768
- 数量：1张

请确认是否生成（请回复 yes 或 no）：
用户：yes
你：[调用 generate_image] 已生成 1 张图片...

记住：始终等待用户明确确认！
""",
        "tools": tools,
    }


def _get_tts_sub_agent(tools: list) -> dict:
    """TTS 子智能体"""
    return {
        "name": "tts-agent",
        "description": "TTS 助手，负责生成语音",
        "system_prompt": """你是一个 TTS（文本转语音）助手，负责帮助用户生成语音。


你必须严格遵守以下流程，任何时候都不能跳过或省略：

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - tts_content: 语音文案（必需）
   - voice_sample_url: 语音样本文件URL（可选，不提供则使用默认语音）

2. **校验信息**：
   - 使用 validate_tts_params 工具验证参数
   - 确保 tts_content 已填写

3. **展示信息并请求确认**（必须步骤）：
   校验通过后，向用户展示以下信息并明确请求确认：
   ```
   准备生成 TTS 语音：
   - 文案：{tts_content}
   - 语音：{voice_sample_url or "使用默认语音"}

   请确认是否生成（请回复 yes 或 no）：
   ```

4. **等待用户明确确认**：
   - ⚠️ 在此步骤必须停止，等待用户回复
   - 只有收到以下明确肯定回复后才能继续：yes、是、好的、确认、同意、可以
   - 如果收到：no、不、不要、取消，则询问是否需要修改
   - ⚠️ 在收到用户明确确认前，绝对不能调用 generate_tts 工具

5. **执行生成**：
   - 只有在用户明确回复 "yes"、"是"、"好的"、"确认"、"同意"、"可以" 等肯定词后，才调用 generate_tts 工具

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- voice_sample_url 是可选的，如果用户不提供，使用默认语音
- 在信息收集完成后，先进行校验
- 校验通过后，展示信息并请求用户确认
- ⚠️ 最重要：必须等待用户明确确认（yes/是/好的/确认/同意）才能调用 generate_tts
- 如果用户没有明确确认，继续等待，不要执行任何工具调用

## 对话示例：

用户：帮我生成语音
你：好的，我可以帮您生成语音。请问语音文案是什么？
用户：你好世界
你：[调用 validate_tts_params 校验参数]

准备生成 TTS 语音：
- 文案：你好世界
- 语音：使用默认语音

请确认是否生成（请回复 yes 或 no）：
用户：yes
你：[调用 generate_tts] 已生成 TTS 语音...

记住：始终等待用户明确确认！
""",
        "tools": tools,
    }


def _get_weather_sub_agent(tools: list) -> dict:
    """天气查询子智能体"""
    return {
        "name": "weather-agent",
        "description": "天气查询助手，负责查询天气",
        "system_prompt": """你是一个天气查询助手，负责帮助用户查询天气。

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
""",
        "tools": tools,
    }


def _get_digital_human_sub_agent(tools: list) -> dict:
    """数字人子智能体"""
    return {
        "name": "digital-human-agent",
        "description": "数字人制作助手，负责制作数字人视频",
        "system_prompt": """你是一个数字人制作助手，负责帮助用户制作数字人视频。

## ⚠️ 最高优先级规则：

**绝对禁止在未收到用户明确确认前调用 create_digital_human 工具！**

## 你的职责：

1. **收集信息**：通过多轮对话收集以下信息：
   - digital_image: 数字人图片（必需）
   - digital_content: 数字人口播文稿（必需）
   - digital_sample: 数字人口播声音样本URL（可选，不提供则使用默认声音）

2. **校验信息**：
   - 使用 validate_digital_human_params 工具验证参数
   - 确保所有必填字段都已填写

3. **展示信息并请求确认**：
   校验通过后，向用户展示以下信息：
   ```
   准备制作数字人视频：
   - 数字人图片：{digital_image}
   - 口播文稿：{digital_content}
   - 声音样本：{digital_sample or "使用默认声音"}

   请确认是否制作（请回复 yes 或 no）：
   ```

4. **等待用户明确确认**：
   - ⚠️ 必须停止，等待用户回复
   - 只有收到：yes、是、好的、确认、同意、可以，才能继续
   - 如果收到：no、不、不要、取消，则询问是否需要修改
   - ⚠️ 在收到用户明确确认前，绝对不能调用 create_digital_human 工具

5. **执行制作**：
   - 只有在用户明确确认后，才调用 create_digital_human 工具

## 重要提示：

- 每次只收集一个字段的信息
- 保持对话友好和自然
- digital_sample 是可选的，如果用户不提供，使用默认声音
- 在信息收集完成后，先进行校验
- 校验通过后，展示信息并请求用户确认
- ⚠️ 必须等待用户明确确认（yes/是/好的/确认/同意）才能调用 create_digital_human
""",
        "tools": tools,
    }


# ==================== 主图构建 ====================

class MasterSubAgent(BaseAgent):
    """主控+子智能体系统

    使用 SubAgentMiddleware 实现主控智能体和多个子智能体协作
    """

    name = "主控+子智能体系统"
    description = "使用主控智能体协调多个子智能体完成邮件、图片生成、TTS、天气查询、数字人等任务"
    context_schema = MasterSubContext
    capabilities = ["file_upload", "todo", "files"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph = None
        self.checkpointer = None

    async def get_graph(self, **kwargs) -> CompiledStateGraph:
        """构建主控+子智能体图"""
        # 获取上下文配置
        context = self.context_schema.from_file(module_name=self.module_name)

        # 加载模型
        model = load_chat_model(context.model)
        sub_model = load_chat_model(context.subagents_model)

        # 获取所有工具（主控智能体使用）
        all_tools = get_master_sub_tools()

        # 获取各子智能体的工具集
        mail_agent_tools = get_mail_agent_tools()
        image_agent_tools = get_image_agent_tools()
        tts_agent_tools = get_tts_agent_tools()
        weather_agent_tools = get_weather_agent_tools()
        digital_human_agent_tools = get_digital_human_agent_tools()

        # 获取所有 MCP 工具
        all_mcp_tools = await get_tools_from_all_servers()

        # 构建子智能体（使用各自的工具集）
        mail_sub_agent = _get_mail_sub_agent(mail_agent_tools)
        image_sub_agent = _get_image_sub_agent(image_agent_tools)
        tts_sub_agent = _get_tts_sub_agent(tts_agent_tools)
        weather_sub_agent = _get_weather_sub_agent(weather_agent_tools)
        digital_human_sub_agent = _get_digital_human_sub_agent(digital_human_agent_tools)

        # 子智能体列表
        subagents = [
            mail_sub_agent,
            image_sub_agent,
            tts_sub_agent,
            weather_sub_agent,
            digital_human_sub_agent,
        ]

        # 创建 SubAgentMiddleware
        subagents_middleware = SubAgentMiddleware(
            default_model=sub_model,
            # default_tools=all_tools,
            subagents=subagents,
            default_middleware=[
                RuntimeConfigMiddleware(
                    model_context_name="subagents_model",
                    enable_model_override=True,
                    enable_system_prompt_override=False,
                    enable_tools_override=False,
                ),
                PatchToolCallsMiddleware(),
            ],
            general_purpose_agent=False,  # 不使用通用智能体
        )

        # 使用 create_agent 创建智能体
        graph = create_agent(
            model=model,
            system_prompt=context.system_prompt,
            middleware=[
                FilesystemMiddleware(backend=_create_fs_backend),  # 文件系统后端
                RuntimeConfigMiddleware(extra_tools=all_mcp_tools),  # 运行时配置应用
                save_attachments_to_fs,  # 附件注入提示词
                TodoListMiddleware(),  # TODO 列表中间件
                PatchToolCallsMiddleware(),  # 工具调用补丁
                subagents_middleware,  # 子智能体中间件
                # 工具调用限制：防止无限循环
                ToolCallLimitMiddleware(
                    run_limit=50,
                    exit_behavior="end",
                ),
            ],
            checkpointer=await self._get_checkpointer(),
        )

        return graph
