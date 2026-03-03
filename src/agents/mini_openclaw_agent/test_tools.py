"""TODO management tools for task planning and progress tracking.

This module provides tools for creating and managing structured task lists
that enable agents to plan complex workflows and track progress through
multi-step operations.
"""
import requests
from typing import Annotated
import os
from langchain_core.messages import ToolMessage,AIMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from src.utils.logging_config import logger

from src.utils import logger
KB_API_BASE_URL = os.getenv("KB_API_BASE_URL")



@tool
def test_create_account_tool(
        accountInfo: str
) -> str:
    """本方法用于用户账号创建
    Args:
        accountInfo: 用户创建用户账号的信息

    Returns:
        知识库返回的相关知识信息 json格式
    """

    logger.info(f"****======>test_create_account_tool accountInfo : {accountInfo} ")
    # logger.info(f"****======>the last message form content : {messages[-3].content}")

    #从message 中找到知识库方法的最近对话
    result_message="账号创建成功!"
    return result_message

@tool()
def test_user_require_check_tool(
        fields_json: str
) -> str:
    """本方法用户 用户输入信息检查
    Args:
        fields_json
        tool_call_id: Injected tool call identifier for message tracking
    # Returns:
    #     Formatted string representation of the current read kb
    """


    result=f"报谦....知识库中暂无  的相关报告"
    logger.info(f"result: {result}")
    return None
