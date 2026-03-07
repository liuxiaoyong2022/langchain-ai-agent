import os
import uuid
from typing import Any

import requests
from langchain.tools import tool

from src.agents.common import get_buildin_tools
from src.agents.common.toolkits.mysql import get_mysql_tools
from src.storage.minio import aupload_file_to_minio
# from src.agents.weatherquery.graph import  WeatherAgent
from src.utils import logger
from mcp.server.fastmcp import FastMCP
from langgraph.types import Command, interrupt
import time
@tool
def send_email(to: str,subject: str, body: str)-> str:
    """
      Args:
        to: The mail of receiver  (e.g., "alice@example.com")
        subject:
        body: the mail content
    """

    logger.info(f"****------>1 即将进入中断 to: {to} ,subject: {subject}, body: {body}")
    # Pause before sending; payload surfaces in result["__interrupt__"]
    response = interrupt({
        "action": "send_email",
        "to": to,
        "subject": subject,
        "body": body,
        "message": "Approve sending this email?",
    })
    logger.info(f"****------>1.1 从中断中恢复 action=={response}")
    user_action=response["decisions"][0]["type"]
    logger.info(f"****------>1.2 从中断中恢复 user_action=={user_action}")
    # if response == True:
    if user_action == "approve":
        final_to = response.get("to", to)
        final_subject = response.get("subject", subject)
        final_body = response.get("body", body)
        #等特 5秒 模拟邮件发送
        time.sleep(5)
        # Actually send the email (your implementation here)
        logger.info(f"****------>1.3 执行确认的邮件发送任务 final_to:{final_to}, final_subject:{final_subject}, final_body:{final_body} ")
        return f"Email succeed send to {to}"
    else:
        logger.info(f"****------>1.4 用户取消的邮件发送任务 action:{response.get("action")} ")
        return "sending Email apply has denied by user"





def get_mail_agent_tools() -> list[Any]:
    """获取sendmail工具列表"""
    return [send_email]
