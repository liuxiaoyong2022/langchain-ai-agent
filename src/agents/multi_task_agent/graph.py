"""Multi-Task Agent Graph - 多任务智能体图构建

基于 create_agent 的实现，参考 deep_agent 的架构
"""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from src.agents.common import BaseAgent, load_chat_model
from src.agents.common.backends import create_agent_composite_backend
from src.agents.common.middlewares import (
    RuntimeConfigMiddleware,
    save_attachments_to_fs,
)
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from langchain.agents.middleware import TodoListMiddleware
from src.services.mcp_service import get_tools_from_all_servers
from src.agents.multi_task_agent.context import MultiTaskContext
from src.agents.multi_task_agent.tools import get_multi_task_tools


def _create_fs_backend(rt):
    """创建文件存储后端"""
    return create_agent_composite_backend(rt)


class MultiTaskAgent(BaseAgent):
    """多任务协作智能体

    使用 create_agent 和工具模式实现的多任务处理系统
    """

    name = "多任务协作智能体"
    description = "具备邮件、图片生成、TTS、天气查询、数字人等多任务处理能力的智能体系统"
    context_schema = MultiTaskContext
    capabilities = ["file_upload", "todo", "files"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph = None

    async def get_graph(self, **kwargs) -> CompiledStateGraph:
        """构建多任务智能体图"""
        if self.graph:
            return self.graph

        # 获取上下文配置
        context = self.context_schema.from_file(module_name=self.module_name)

        # 加载模型
        model = load_chat_model(context.model)

        # 获取多任务工具
        multi_task_tools = get_multi_task_tools()

        # 获取所有 MCP 工具
        all_mcp_tools = await get_tools_from_all_servers()

        # 使用 create_agent 创建智能体（参考 deep_agent 的实现）
        graph = create_agent(
            model=model,
            system_prompt=context.system_prompt,
            tools=multi_task_tools,
            middleware=[
                FilesystemMiddleware(backend=_create_fs_backend),  # 文件系统后端（第一位）
                RuntimeConfigMiddleware(extra_tools=all_mcp_tools),  # 运行时配置应用
                save_attachments_to_fs,  # 附件注入提示词
                TodoListMiddleware(),  # TODO 列表中间件
                PatchToolCallsMiddleware(),  # 工具调用补丁
            ],
            checkpointer=await self._get_checkpointer(),
        )

        self.graph = graph
        return self.graph
