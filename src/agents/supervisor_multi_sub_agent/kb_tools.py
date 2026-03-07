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
from .prompts import WRITE_TODOS_DESCRIPTION
from .state import DeepAgentState, Todo
from fastapi import APIRouter, Depends, HTTPException, Query
from .prompts import KB_SUB_AGENT_DESCRIPTION,KB_SUB_AGENT_INSTRUCTIONS
from src.utils import logger
KB_API_BASE_URL = os.getenv("KB_API_BASE_URL")


@tool(description=KB_SUB_AGENT_DESCRIPTION)
# @tool
def kb_query_tool(
        state: Annotated[DeepAgentState, InjectedState],
        query: str
) -> str:
    """通过关键字进行本地汽车知识查询
    Args:
        state: Injected agent state for var storage
        query: 用于汽车知识检索和匹配的查询关键字,或查询字符串
    Returns:
        知识库返回的相关知识信息 json格式
    """
    messages=state.get("messages")
    messages_length=len(messages)
    logger.info(f"****======>0 kb 获取上下文 message length : {messages_length} ,messages : {messages}")
    # logger.info(f"****======>the last message form content : {messages[-3].content}")

    #从message 中找到知识库方法的最近对话
    messages_index = messages_length - 1
    max_chat_count = 3
    conversation_history = []
    while messages_index > 0 and max_chat_count>0:
        current_message=messages[messages_index]
        if isinstance(current_message , ToolMessage) and current_message.name.strip().startswith("kb_query_too"):

            logger.info(f"****1====> find ToolMessage content: {current_message.content}")
            logger.info(f"****1====> find ToolMessage name: {current_message.name}")
            tool_call_id=current_message.tool_call_id
            logger.info(f"****1====> find ToolMessage tool_call_id: {tool_call_id}")
            # 根据tool_call_id 找到对应的 ask AIMessage
            askMessage_index=messages_index - 1
            while askMessage_index > 0:
                # logger.info(f"**** morniter ====> askMessage_index: {askMessage_index}")
                ask_message=messages[askMessage_index]
                if isinstance(ask_message, AIMessage) and ask_message.tool_calls:
                    # tool_calls=ask_message.tool_calls
                    for index, tool_call in enumerate(ask_message.tool_calls):
                        if(tool_call.get('id')==tool_call_id):
                            args=tool_call.get("args")
                            logger.info(f"====> find ask AIMessage   args:{args.get("query")}")
                            conversation_history.append({
                                "role": "user",
                                "content": args.get("query")
                                })
                            conversation_history.append(
                                {"role": "assistant",
                                 "content": current_message.content
                                })
                            #只保留最近3次对话
                            max_chat_count -=1
                            #退出当前  for loop
                            break
                            #退出当前的一次查找 while loop
                            break
                    # logger.info(f"---->1 find finish ask AIMessage")
                askMessage_index -= 1
            # logger.info(f"---->2 find finish ask AIMessage")
        messages_index -= 1


    # if messages_length >3 and messages_length<=6:
        # 这里取最一次对话历史记录
        # logger.info(f"****======>the last message form content : {messages[-3].content}")
        # logger.info(f"****======>the last message form usage_metadata : {messages[-3].usage_metadata}")


    logger.info(f"****======>conversation_history : {conversation_history}")
    # Define the API endpoint URL
    url = f'{KB_API_BASE_URL}/query'
    query_body = {
        "query": query,
        "mode": "local",
        "conversation_history":conversation_history
    }
    logger.info(f"------> query:{query_body}")
    try:
        headers = {'Content-Type': 'application/json'}
        response =  requests.post(url, json=query_body,headers=headers)
        logger.info(f"------> response:{response}")
        if response.status_code == 200:
            result = response.json()
            #log response字段
            logger.info(f"result['response']================>:{result['response']}")
            return result
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        raise HTTPException(status_code=400, detail=f"知识库接口调用异常:{e}")
    return "success"

# @tool()
def kb_list_doc_tool(
        tool_call_id: Annotated[str, InjectedToolCallId],
) -> str:
    """查旬当前本地知库已有的文档信息
    Args:
        # file_path: 要获取内容的目标文件路径
        tool_call_id: Injected tool call identifier for message tracking
    # Returns:
    #     Formatted string representation of the current read kb
    """

    logger.info(f"---------->tool_call_id:{tool_call_id}")
    # Define the API endpoint URL
    url = f'{KB_API_BASE_URL}/documents'
    logger.info(f"---------->url:{url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        raise HTTPException(status_code=400, detail=f"知识库接口调用异常:{e}")

    # return result.strip()
