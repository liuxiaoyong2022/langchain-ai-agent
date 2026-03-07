from langchain.agents import create_agent

from src import config
from src.agents.common import BaseAgent, load_chat_model
from src.agents.common.middlewares import context_aware_prompt, context_based_model
from src.agents.mail_agent.tools import get_mail_agent_tools
from src.utils import logger

# _mcp_servers = {"mcp-sendmail": {"url": "http://localhost:8000/mcp",  "transport": "streamable_http"}}
# _mcp_servers = {"mcp-server-sendmail": {"command": "python", "args": [str(current_dir / "send-mail-tool.py")], "transport": "stdio"}}

class MailSendAgent(BaseAgent):
    name = "邮件发送智能助手"
    description = "一个能够邮件接收且邮件发送的智能体助手。 "
    send_mail_instructions = """
    您是一位资深的邮件发送专员。您的工作是在检查邮件信息是否完整,并能发在发送前检查邮件内容。
    邮件完整性检查,从用户的输入中提取以下信息
         1. 收件人邮箱{mail_address}
         2. 邮件主题{mail_topic}
         3. 邮件内容{mail_content}
    要求：
   - 需要通过多轮对话引导用户输入缺失信息
   - 每次只问一个缺失信息信的问题  比如: 请您提供 收件人邮箱 或 请你输入邮件内容 让用户提供相应信息
   - 如果已经收集到某个信息，就不要重复询问
   - 每次回复要简洁,不要过多建议
   - 当所有信息收集完成后，总结并结束对话
   当前已知信息：
   {history}
   用户输入：
   {input}     


    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_tools(self):
        logger.info(f"**** ---->entered send mail  get_tools")
        # weather_tools = await get_mcp_tools("mcp-server-sendmail", additional_servers=_mcp_servers)
        # mysql_tools = get_mysql_tools()
        tools = get_mail_agent_tools()
        logger.info(f"**** ---->send-mail-tools:{tools}")
        return tools

    async def get_graph(self, **kwargs):
        if self.graph:
            return self.graph

        # 创建 SqlReporterAgent
        graph = create_agent(
            model=load_chat_model(config.default_model),  # 默认模型，会被 middleware 覆盖
            system_prompt=self.send_mail_instructions,
            tools=await self.get_tools(),
            middleware=[context_aware_prompt, context_based_model],
            checkpointer=await self._get_checkpointer(),
        )

        self.graph = graph
        logger.info("MailSendAgent 构建成功")
        return graph
