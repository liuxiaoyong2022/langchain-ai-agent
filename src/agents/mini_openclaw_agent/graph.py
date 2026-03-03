from langchain.agents import create_agent

from src import config
from src.agents.common import BaseAgent, get_buildin_tools, load_chat_model
from src.agents.common.middlewares import context_aware_prompt, context_based_model
from src.agents.mini_openclaw_agent.memory.prompt_builder import PromptBuilder
from src.agents.mini_openclaw_agent.tools.core_tools import initialize_core_tools
import os
from pathlib import Path
from langchain.agents.middleware import ModelRequest, dynamic_prompt,before_model


# @dynamic_prompt
# def context_aware_prompt(request: ModelRequest) -> str:
#     """从 runtime context 动态生成系统提示词"""
#     context = request.runtime.context
#     print(f" context_aware_prompt request---->{request}")
#     return  "\n\n\n" + request.runtime.context.system_prompt


class MiniOpenClawAgent(BaseAgent):
    name = "mini_openClaw智能体"
    description = "一个模仿mini-open-claw 有一定skill能力的智能体示例"


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"MiniOpenClawAgent   init---------->   current_dir:{current_dir}")
        self.project_root=Path(current_dir)


    def get_tools(self):
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"  MiniOpenClawAgent---------->   self.project_root:{self.project_root}")
        mini_open_claw_tools = initialize_core_tools(self.project_root)
        return mini_open_claw_tools   #get_buildin_tools()

    async def get_graph(self, **kwargs):
        if self.graph:
            return self.graph

        # 初始化 Prompt Builder
        # self.prompt_builder = PromptBuilder(
        #     workspace_dir= "backend" / "workspace",
        #     memory_dir= "backend" / "memory",
        #     skills_dir= "backend" / "skills"
        # )
        print(f"  MiniOpenClawAgent----------> self.project_root:{self.project_root}")
        self.prompt_builder = PromptBuilder(
            workspace_dir=self.project_root / "workspace",
            memory_dir=self.project_root / "memory",
            skills_dir=self.project_root / "skills"
        )


        # self.prompt_builder = PromptBuilder(
        #     workspace_dir=self.project_root / "backend" / "workspace",
        #     memory_dir=self.project_root / "backend" / "memory",
        #     skills_dir=self.project_root / "backend" / "skills"
        # )

        # 构建 System Prompt
        self.system_prompt = self.prompt_builder.build_system_prompt()
        print(f"  MiniOpenClawAgent---------->   system_prompt:{self.system_prompt}")

        # 使用 LangGraph 的 create_agent
        # 这是 LangChain 1.2.6 + LangGraph 1.0.7 的标准方式
        graph = create_agent(
            model=load_chat_model(config.default_model),
            tools=self.get_tools(),
            system_prompt=self.system_prompt,  # 注入 System Prompt
            checkpointer=await self._get_checkpointer(),
            # middleware=[context_aware_prompt],
        )

        # 创建 MiniAgent
        # graph = create_agent(
        #     model=load_chat_model(config.default_model),  # 实际会被覆盖
        #     tools=self.get_tools(),
        #     # middleware=[context_aware_prompt, context_based_model],
        #     checkpointer=await self._get_checkpointer(),
        # )

        self.graph = graph
        return graph
