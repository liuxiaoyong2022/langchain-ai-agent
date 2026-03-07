"""Deep Agent - 基于create_deep_agent的深度分析智能体"""
from src.agents.common import BaseAgent
from deepagents import create_deep_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from datetime import datetime
from langchain.agents.middleware import HumanInTheLoopMiddleware
from src.agents.common import BaseAgent, load_chat_model
from src.agents.common.middlewares import context_based_model, inject_attachment_context
from .master_tools import create_task_plan,analyze_user_input
from .tools import calculator_wstate,think_tool
from .file_tools import ls, read_file, write_file
from .todo_tools import write_todos, read_todos
from .kb_tools import kb_query_tool, kb_list_doc_tool
from .car_home_tools import car_home_tool_doc_query,car_home_tool_bbs_query,car_home_tool_process_search_results
from .mail_tools import send_email,validate_email,search_email
from .content_generate_tools import generate_content_for_car,batch_wash_docs ,generate_pure_txt_content
from .weather_tool import get_weather,get_forecast,compare_weather,get_weather_alerts
from .tts_tools import text_to_speech,generate_audio_script,batch_text_to_speech
# from .video_tools import digital_human_video_gen_tool
from .digital_human_tools import digital_human_img_generate
from .image_tools import generate_image
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from .prompts import (
    TODO_USAGE_INSTRUCTIONS,
                      # FILE_USAGE_INSTRUCTIONS,
                      # MATH_INSTRUCTIONS,
                      # WEATHER_INSTRUCTIONS,
                      # KB_INSTRUCTIONS,
                      # CRITIQUE_INSTRUCTIONS,
COLLECT_INFO_INSTRUCTIONS,
    FILE_USAGE_INSTRUCTIONS,
    WRITE_TODOS_DESCRIPTION,
    TASK_ANALYSIS_AND_PLAN,
    # RESEARCHER_INSTRUCTIONS,
    # SUBAGENT_USAGE_INSTRUCTIONS,
    TODO_USAGE_INSTRUCTIONS,
    MATH_SUB_AGENT_INSTRUCTIONS,
    MATH_SUB_AGENT_DESCRIPTION,
    WEATHER_SUB_AGENT_INSTRUCTIONS,
    WEATHER_SUB_AGENT_DESCRIPTION,
    MAIL_SUB_AGENT_INSTRUCTIONS,
    MAIL_SUB_AGENT_DESCRIPTION,
    KB_SUB_AGENT_INSTRUCTIONS,
    KB_SUB_AGENT_DESCRIPTION,
    CAR_HOME_SUB_AGENT_DESCRIPTION,
    CAR_HOME_SUB_AGENT_INSTRUCTIONS,
    SUB_AGENTS_USAGE_INSTRUCTIONS,

    CRITIQUE_INSTRUCTIONS,
    CRITIQUE_SYSTEM_PROMPT,
    CONTENT_GENERATE_SUB_AGENT_DESCRIPTION,
    CONTENT_GENERATE_SUB_AGENT_INSTRUCTIONS,
    DIGITAL_HUMAN_CREATOR_SUB_AGENT_DESCRIPTION,
    DIGITAL_HUMAN_CREATOR_SUB_AGENT_INSTRUCTIONS,
    TTS_SUB_AGENT_DESCRIPTION,
    TTS_SUB_AGENT_INSTRUCTIONS,
    VIDEO_SUB_AGENT_DESCRIPTION,
    VIDEO_SUB_AGENT_INSTRUCTIONS,
    DIGITAL_HUMAN_VIDEO_SUB_AGENT_DESCRIPTION,
    DIGITAL_HUMAN_VIDEO_SUB_AGENT_INSTRUCTIONS,
    SIMPLE_TXT_CONTENT_GENERATE_SUB_AGENT_DESCRIPTION,
    SIMPLE_TXT_CONTENT_GENERATE_SUB_AGENT_INSTRUCTIONS,
IMAGE_SUB_AGENT_DESCRIPTION,
IMAGE_SUB_AGENT_INSTRUCTIONS,
COLLECT_INFO_SUB_AGENT_DESCRIPTION,
COLLECT_INFO_SUB_AGENT_INSTRUCTIONS,
)
from .context import SUPERVISOR_PROMPT
from src.utils import logger

# search_tools = [process_search_results]
# search_tools = [search]
math_sub_agent_tools= [calculator_wstate]
kb_sub_agent_tools = [kb_query_tool]
car_home_sub_agent_tools =[car_home_tool_doc_query,car_home_tool_bbs_query,car_home_tool_process_search_results]
mail_sub_agent_tools =[send_email,validate_email,search_email]
master_agent_tools =[analyze_user_input,create_task_plan]
weather_sub_agent_tools= [get_weather,get_forecast,compare_weather,get_weather_alerts]
content_generate_sub_agent_tools =[generate_content_for_car,batch_wash_docs]
simple_content_generate_sub_agent_tools =[
    generate_pure_txt_content
]
image_sub_agent_tools=[generate_image ]
digital_human_creator_sub_agent_tools =[
                                        # digital_human_material_check_tool,
                                        # digital_human_img_generate,
                                        # generate_pure_txt_content,
                                        # tts_txt_to_audio_tool,
                                        # digital_human_video_gen_tool
                                        ]
digital_human_video_sub_agent_tools =[
    # generate_pure_txt_content,
    # tts_txt_to_audio_tool,
    # digital_human_video_gen_tool,
    digital_human_img_generate,
                                      ]

tts_sub_agent_tools =[
                      text_to_speech,
                      generate_audio_script,
                      batch_text_to_speech]
# video_sub_agent_tools = [digital_human_video_gen_tool]

math_sub_agent = {
    "name": "math_sub_agent",
    "description": MATH_SUB_AGENT_DESCRIPTION,
    "system_prompt": MATH_SUB_AGENT_INSTRUCTIONS,
    "tools": math_sub_agent_tools,
}

weather_sub_agent = {
    "name": "weather_sub_agent",
    "description": WEATHER_SUB_AGENT_DESCRIPTION,
    "system_prompt": WEATHER_SUB_AGENT_INSTRUCTIONS,
    "tools": weather_sub_agent_tools,
}

mail_sub_agent = {
    "name": "mail_sub_agent",
    "description": MAIL_SUB_AGENT_DESCRIPTION,
    "system_prompt": MAIL_SUB_AGENT_INSTRUCTIONS,
    "tools": mail_sub_agent_tools,
    "interrupt_on": {
            # Override: require approval for reads in this subagent
            "send_email": {
                    "allowed_decisions": ["approve", "reject"],
                },
    
        }
}
kb_sub_agent = {
    "name": "kb_sub_agent",
    "description": KB_SUB_AGENT_DESCRIPTION,
    "system_prompt": KB_SUB_AGENT_INSTRUCTIONS,
    "tools": kb_sub_agent_tools,
    "model": load_chat_model("dashscope/qwen-max-latest"),
}
car_home_sub_agent = {
    "name": "car_home_sub_agent",
    "description": CAR_HOME_SUB_AGENT_DESCRIPTION,
    "system_prompt": CAR_HOME_SUB_AGENT_INSTRUCTIONS,
    "tools": car_home_sub_agent_tools,
}

content_generate_sub_agent = {
    "name": "content_generate_sub_agent",
    "description": CONTENT_GENERATE_SUB_AGENT_DESCRIPTION,
    "system_prompt": CONTENT_GENERATE_SUB_AGENT_INSTRUCTIONS,
    "tools": content_generate_sub_agent_tools,
}

simple_content_generate_sub_agent = {
    "name": "simple_content_generate_sub_agent",
    "description": SIMPLE_TXT_CONTENT_GENERATE_SUB_AGENT_DESCRIPTION,
    "system_prompt": SIMPLE_TXT_CONTENT_GENERATE_SUB_AGENT_INSTRUCTIONS,
    "tools": simple_content_generate_sub_agent_tools,
}

digital_human_creator_sub_agent = {
    "name": "digital_human_creator_sub_agent",
    "description": DIGITAL_HUMAN_CREATOR_SUB_AGENT_DESCRIPTION,
    "system_prompt": DIGITAL_HUMAN_CREATOR_SUB_AGENT_INSTRUCTIONS,
    "tools": digital_human_creator_sub_agent_tools,
    # "interrupt_on": {
    #         # Override: require approval for reads in this subagent
    #         "digital_human_material_check_tool": {
    #                 "allowed_decisions": ["approve", "reject"],
    #             },
    #
    #     }

}

digital_human_video_sub_agent = {
    "name": "digital_human_video_sub_agent",
    "description": DIGITAL_HUMAN_VIDEO_SUB_AGENT_DESCRIPTION,
    "system_prompt": DIGITAL_HUMAN_VIDEO_SUB_AGENT_INSTRUCTIONS,
    "tools": digital_human_video_sub_agent_tools,

}

tts_sub_agent = {
    "name": "tts_sub_agent",
    "description": TTS_SUB_AGENT_DESCRIPTION,
    "system_prompt": TTS_SUB_AGENT_INSTRUCTIONS,
    "tools": tts_sub_agent_tools,
}

# video_sub_agent = {
#     "name": "video_sub_agent",
#     "description": VIDEO_SUB_AGENT_DESCRIPTION,
#     "system_prompt": VIDEO_SUB_AGENT_INSTRUCTIONS,
#     "tools": video_sub_agent_tools,
# }
image_sub_agent = {
    "name": "image_sub_agent",
    "description": IMAGE_SUB_AGENT_DESCRIPTION,
    "system_prompt": IMAGE_SUB_AGENT_INSTRUCTIONS,
    "tools": image_sub_agent_tools,
}






# critique_sub_agent = {
#     "name": "critique-agent",
#     "description": CRITIQUE_INSTRUCTIONS,
#     "system_prompt": CRITIQUE_SYSTEM_PROMPT,
#    # "tools": sub_critique_tools,
# }


@dynamic_prompt
def context_aware_prompt(request: ModelRequest) -> str:
    """从 runtime context 动态生成系统提示词"""
    return SUPERVISOR_PROMPT + "\n\n\n" + request.runtime.context.system_prompt


# @dynamic_prompt
# def context_aware_prompt(request: ModelRequest) -> str:
#     """从 runtime context 动态生成系统提示词"""
#     return DEEP_PROMPT + "\n\n\n" + request.runtime.context.system_prompt
# Build prompt

max_concurrent_research_units = 3
max_researcher_iterations = 3
# SUBAGENT_INSTRUCTIONS = SUBAGENT_USAGE_INSTRUCTIONS.format(
#     max_concurrent_research_units=max_concurrent_research_units,
#     max_researcher_iterations=max_researcher_iterations,
#     date=datetime.now().strftime("%a %b %-d, %Y"),
# )

INSTRUCTIONS = (
    "# TODO MANAGEMENT\n"
    + TODO_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# FILE SYSTEM USAGE\n"
    + FILE_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# WRITE_TODOS_DESCRIPTION \n"
    + WRITE_TODOS_DESCRIPTION
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# TASK_ANALYSIS_AND_PLAN\n"
    + TASK_ANALYSIS_AND_PLAN
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + "# COLLECT_INFO\n"
    + COLLECT_INFO_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    # + "# WEATHER-SUB-AGENT Weather-reporter\n"
    # + WEATHER_SUB_AGENT_DESCRIPTION
    # + "\n\n"
    # + "=" * 80
    # + "\n\n"
    # + "# KB_SUB_AGENT Knowledge-base\n"
    # + KB_SUB_AGENT_INSTRUCTIONS
    # + "\n\n"
    # + "=" * 80
    # + "\n\n"
    # + "# CAR-HOME-SUB-AGENT \n"
    # + CAR_HOME_SUB_AGENT_DESCRIPTION
    # + "\n\n"
    # + "=" * 80
    # + "\n\n"
    # + "# CONTENT-GENERATE-SUB-AGENT \n"
    # + CONTENT_GENERATE_SUB_AGENT_DESCRIPTION
    # + "\n\n"
    # + "=" * 80
    # + "\n\n"

)



class SupervisorAgent(BaseAgent):
    name = "任务调度智能体"
    description = "该智能体具备规划、深度分析和子智能体协作能力的智能体，可以处理复杂的多步骤任务"
    capabilities = [
        "file_upload",
        "todo",
        "files",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph = None
        self.checkpointer = None

    # _mcp_servers = {"mcp-weather": {"url": "http://localhost:8000/mcp",  "transport": "streamable_http"}}

    # async def get_weather_tools(self):
    #     logger.info(f"**** ---->entered weather  get_tools")
    #     weather_tools = await get_mcp_tools("mcp-weather", additional_servers=_mcp_servers)
    #     # mysql_tools = get_mysql_tools()
    #     logger.info(f"**** ---->weather-tools:{weather_tools}")
    #     return weather_tools



    async def get_tools(self):
        """返回 Deep Agent 的专用工具"""

        built_in_tools = [ls, read_file, write_file, write_todos, read_todos]
        # weather_tool= await self.get_weather_tools()

        # tools = built_in_tools
        tools = (built_in_tools
                 + master_agent_tools
                 # + weather_sub_agent_tools
                 # + kb_sub_agent_tools
                 # + car_home_sub_agent_tools
                 # + content_generate_sub_agent_tools

                 )
        # tools = search_tools
        return tools

    async def get_graph(self, **kwargs):
        """构建 Deep Agent 的图"""
        if self.graph:
            return self.graph

        # 获取上下文配置
        context = self.context_schema.from_file(module_name=self.module_name)
        # weather_tool = await get_weather_tools()

        # 使用 create_deep_agent 创建深度智能体
        graph = create_deep_agent(
            model=load_chat_model(context.model),
            tools=await self.get_tools(),
            subagents=[
                        math_sub_agent,
                        mail_sub_agent,
                        image_sub_agent,
                        # weather_sub_agent,
                        # kb_sub_agent,
                        # car_home_sub_agent,
            
                        tts_sub_agent,       
            ],
            system_prompt=INSTRUCTIONS,
            # subagents=[critique_sub_agent, research_sub_agent],
            middleware=[
                context_based_model,  # 动态模型选择
                # context_aware_prompt,  # 动态系统提示词
                inject_attachment_context,  # 附件上下文注入

            ],
            checkpointer=await self._get_checkpointer(),
        )

        self.graph = graph
        return graph
