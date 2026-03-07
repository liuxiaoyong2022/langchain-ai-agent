import os
import uuid
from typing import Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils import logger
import requests
from langchain.tools import tool
import time
from datetime import datetime
# from src.utils import logger
from mcp.server.fastmcp import FastMCP
from langgraph.types import Command, interrupt
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState

import json
# Configuration for Mailtrap's Bulk SMTP server
smtp_server = "bulk.smtp.mailtrap.io"
port = 587
login = "api"  # Your Mailtrap login
password = "1a2b3c4d5e6f7g"  # Your Mailtrap password

sender_email = "mailtrap@example.com"


# @tool
# def send_email(to: str,subject: str, body: str)-> str:
#     """
#       本工具专门处理具体的邮件发送任务
#       Args:
#         to: The mail of receiver  (e.g., "alice@example.com")
#         subject: 邮件主题
#         body: the mail content
#     """
#
#     logger.info(f"****------>1 即将进入中断 to: {to} ,subject: {subject}, body: {body}")
#     # Pause before sending; payload surfaces in result["__interrupt__"]
#     response = interrupt({
#         "action": "send_email",
#         "to": to,
#         "subject": subject,
#         "body": body,
#         "message": "Approve sending this email?",
#     })
#     logger.info(f"****------>1.1 从中断中恢复 action=={response}")
#     user_action=response["decisions"][0]["type"]
#     logger.info(f"****------>1.2 从中断中恢复 user_action=={user_action}")
#     # if response == True:
#     if user_action == "approve":
#         final_to = response.get("to", to)
#         final_subject = response.get("subject", subject)
#         final_body = response.get("body", body)
#         #等特 5秒 模拟邮件发送
#         time.sleep(5)
#         # Actually send the email (your implementation here)
#         logger.info(f"****------>1.3 执行确认的邮件发送任务 final_to:{final_to}, final_subject:{final_subject}, final_body:{final_body} ")
#         return f"Email succeed send to {to}"
#     else:
#         logger.info(f"****------>1.4 用户取消的邮件发送任务 ")
#         return "sending Email apply has denied by user"

@tool
def validate_email(mail: str) -> str:
        """
        验证邮箱或邮件地址格式是否正确

        Args:
            mail: 需要进行验证的邮箱或邮件地址
        Returns:
           邮箱地址验证结果
        """
        # 模拟搜索功能
        import re

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, mail):
            print(f"--------->email:{mail} 邮箱地址格式正确")
            return json.dumps({
                "mail":mail,
                "action":"validate",
                "success": True,
                "message": "邮箱地址验证成功"

            }, ensure_ascii=False)
            # return f"✅ 邮箱地址格式正确：{email_address}"

        else:
            print(f"--------->email_address:{mail} 邮箱地址格式不正确")
            # return f"❌ 邮箱地址格式不正确：{email_address}"
            return json.dumps({
                "mail": mail,
                "action": "validate",
                "success": False,
                "message": "邮箱地址验证失败",

            }, ensure_ascii=False)


@tool
def send_email(to: str, subject: str, body: str) -> str:
        """
        发送邮件工具,当需要进行邮件发送时可调用该工具

        Args:
            to: 收件人邮箱地址
            subject: 邮件主题
            body: 邮件正文


        Returns:
            发送结果
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = "lxyxd_2001@yahoo.com.cn"
            msg['To'] = to
            msg['Subject'] = subject



            # 添加正文
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            print(f"step 1.3.1--------->mock email send \r\n to:{to}     \r\n subject:{subject} \r\n body:{body} \r\n full email:{msg}")
            mail_send_time=5
            time.sleep(mail_send_time)



            # # 连接SMTP服务器并发送
            # config = EmailAgent._get_config()
            # server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
            # server.starttls()
            # server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
            #
            # recipients = [to]
            # if cc:
            #     recipients.extend(cc.split(','))
            # if bcc:
            #     recipients.extend(bcc.split(','))
            #
            # server.send_message(msg)
            # server.quit()
            mail_send_result={
                "success": True,
                "message": "邮件发送成功",
                "to": to,
                "subject": subject,
                "timestamp": datetime.now().isoformat()
            }
            print(f"step 1.3.2--------->mock email send finished ,mail_send_result:{mail_send_result}")
            return json.dumps(mail_send_result, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"邮件发送失败: {str(e)}",
                "to": to,
                "subject": subject
            }, ensure_ascii=False)


@tool
def search_email(query: str, folder: str = "all") -> str:
        """
        搜索邮件

        Args:
            query: 搜索关键词
            folder: 搜索范围

        Returns:
            搜索结果
        """
        print(f" step 1.7 do mock search_emails--------->  query:{query}  ")
        # 模拟搜索功能
        return json.dumps({
            "success": True,
            "query": query,
            "folder": folder,
            "results": [
                {
                    "id": "001",
                    "from": "sender@example.com",
                    "subject": f"包含'{query}'的邮件",
                    "date": "2025-01-30"
                }
            ]
        }, ensure_ascii=False)