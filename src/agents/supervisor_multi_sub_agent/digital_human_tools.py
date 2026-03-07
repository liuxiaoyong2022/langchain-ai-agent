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
from langgraph.types import Command, interrupt
from fastapi import APIRouter, Depends, HTTPException, Query
from .prompts import KB_SUB_AGENT_DESCRIPTION,KB_SUB_AGENT_INSTRUCTIONS
from src.utils import logger
KB_API_BASE_URL = os.getenv("KB_API_BASE_URL")
import json
from time import sleep
@tool()
def digital_human_material_check_tool(
        human_target: str="数字人播报员",
        content:str="",
        topic:str="",
        human_image_url:str=None,
        voice_sample_url:str=None
) -> str:
    """本工具用检查和准备数字人制作的基本素才
    Args:
        human_target：制作的目标数字人
        content: 数据字人将要播报的文本内容
        topic: 数据字人将要播报信息的主题
        human_image_url: 数字人图像url
        voice_sample_url: 语音样本文件url
    # Returns:
    #     Formatted string representation of the current read kb
    """
    logger.info(f"****------>1 即将进入中断 human_target: {human_target} ,content: {content}  human_image_url:{human_image_url}")

    # Pause before sending; payload surfaces in result["__interrupt__"]
    # response = interrupt({
    #     "action": "digital_human",
    #
    #
    #     "message": "同意这次数字人制作吗",
    # })
    #
    # logger.info(f"****------>1.1 从中断中恢复 action=={response}")
    # result = "approve"
    # if response.get("action") == "approve":
    #     result="approve"
    # else:
    #     result="deny"

    logger.info(f"***=========>do digital_human_material_check_tool voice_sample_url:{voice_sample_url} ,topic:{topic}")
    # Define the API endpoint URL
    result = "approve"
    return result

@tool
def digital_human_img_generate(human_target: str,
                               description:str) -> str:
    """该工具用于根据目标人物 以及描述生成数字人图片，
        Args:

            human_target: 要生成的目标数字人,
            description: 对数字人的要求
        Returns:
            图片访问路径
        """


    url = "https://carbotai.com/api/AI/chat"
    logger.info(f"human_target=============>:{human_target},description:{description} ")
    payload = {
        "content": human_target,
        "model_id": 10,
        "type": "messages",
        "from": 3
    }
    headers = {"X-Auth-Token": f"{os.getenv('LOCAL_IMAGE_GEN_API_KEY')}", "Content-Type": "application/json"}

    # url = "https://api.siliconflow.cn/v1/images/generations"
    # payload = {
    #     "model": "Qwen/Qwen-Image",
    #     "prompt": image_topic,
    # }
    # headers = {"Authorization": f"Bearer {os.getenv('SILICONFLOW_API_KEY')}", "Content-Type": "application/json"}
    # image_url=''
    image_url = 'https://carbotai.com/api/uploads/doubao-1768292925471807850.png'
    with requests.post(url, json=payload, headers=headers, stream=True) as r:
        for line in r.iter_lines(decode_unicode=True):
            logger.info(f"------------>  line:{line}")
            if line.startswith('data:'):
                data = line[5:].strip()
                json_data = json.loads(data)

                logger.info(f"json_data--->: {json_data}")
                temp_url=json_data["data"]
                logger.info(f"temp_url--->: {temp_url}")
                if temp_url.startswith('https'):
                    image_url=temp_url
            elif line.startswith('event:'):
                event_type = line[6:].strip()
                print(f"Event type: {event_type}")
    sleep(5)
    logger.info(f"Digital Human Image URL: {image_url}")
    return image_url