"""
This module provides tools for creating documents about cars
"""
import requests
from typing import Annotated
import os
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from src.utils.logging_config import logger
from .prompts import (CONTENT_GENERATE_PROMPT_TEMPLATE
                      ,IMAGE_GENERATE_INSTRUCTIONS
                      ,CONTENT_GENERATE_PROMPT_XHS_TEMPLATE
                      ,SIMPLE_TXT_CONTENT_GENERATE_SUB_AGENT_INSTRUCTIONS)
from .state import DeepAgentState, Todo
from fastapi import APIRouter, Depends, HTTPException, Query
# from .prompts import KB_INSTRUCTIONS
from src.utils import logger
from langchain.agents import create_agent
from src.agents.common import BaseAgent, load_chat_model
import json
from langgraph.config import get_stream_writer
# @tool
def generate_image_for_content(
        image_topic: str,
        # tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """该工具用于生成内容中的图片，
        Args:

            image_topic: 图片主题，生成图片的依据,
        Returns:
            图片访问路径
        """
    logger.info(f"image topic=============>:{image_topic}")

    iamge_url=f"https://iam.amazonaws.com/{image_topic}"
    logger.info(f"do image generation=============>{iamge_url}")

    return iamge_url

@tool
def text_to_img_local(image_topic: str) -> str:
    """该工具用于生成内容中的图片，
        Args:

            image_topic: 图片主题，生成图片的依据,
        Returns:
            图片访问路径
        """


    url = "https://carbotai.com/api/AI/chat"
    logger.info(f"image topic=============>:{image_topic}")
    payload = {
        "content": image_topic,
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
    image_url=''
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

    # try:
    #     response = requests.post(url, json=payload, headers=headers)
    #     response_json = response.json()
    #     logger.info(f"image response_json=============>:{response_json}")
    # except Exception as e:
    #     logger.error(f"Failed to generate image with Kolors: {e}")
    #     raise ValueError(f"Image generation failed: {e}")

    # try:
    #     image_url = response_json["images"][0]["url"]
    #     logger.info(f"image image_url=============>:{image_url}")
    # except (KeyError, IndexError, TypeError) as e:
    #     logger.error(f"Failed to parse image URL from Kolors response: {e}, {response_json=}")
    #     raise ValueError(f"Image URL extraction failed: {e}")

    # 2. Upload to MinIO (Simplified)
    # response = requests.get(image_url)
    # file_data = response.content
    #
    # file_name = f"{uuid.uuid4()}.jpg"
    # image_url = await aupload_file_to_minio(
    #     bucket_name="generated-images", file_name=file_name, data=file_data, file_extension="jpg"
    # )
    logger.info(f"Image URL: {image_url}")
    return image_url



# default_model="siliconflow/deepseek-ai/DeepSeek-V3.2"
# default_model="local-ollama/cnshenyang/qwen3-nothink:14b"
default_model="deepseek/deepseek-chat"
# default_model="local-ollama-deepseek-r1/MFDoom/deepseek-r1-tool-calling:70b"
content_model=load_chat_model(default_model)
content_generate_agent = create_agent(
    model=content_model,
    tools = [text_to_img_local],
    system_prompt=IMAGE_GENERATE_INSTRUCTIONS
)

pure_content_generate_agent = create_agent(
    model=content_model,

    system_prompt=IMAGE_GENERATE_INSTRUCTIONS
)


@tool
def generate_content_for_car(
        state: Annotated[DeepAgentState, InjectedState],
        topic: str,
        material: str='暂无素材',
        language: str = "中文",
        length: int = 100,
        # tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """该工具用于生成文案内容，包括相应图片或图片链接url
    Args:
        topic: 内容创作的主题
        material: 内容创作的素材,
    Returns:
        最络内容分析报告 json格式
    """

    logger.info(f"topic={topic}, material={material}")
    # Build prompt
    CONTENT_GENERATE_PROMPT = CONTENT_GENERATE_PROMPT_XHS_TEMPLATE.format(
        length=length,
        topic=topic,
        language=language,
        material=material
    )
    logger.info(f"CONTENT_GENERATE_PROMPT=============>:{CONTENT_GENERATE_PROMPT}")
    messages = [
        {
            "role": "user",
            "content": CONTENT_GENERATE_PROMPT,

        }

    ]
    content_generated = content_generate_agent.invoke({
        "messages": messages,
    },)
    # Define the API endpoint URL
    logger.info(f"content_generated=============>:{content_generated}")

    return content_generated


@tool
def generate_pure_txt_content(
        state: Annotated[DeepAgentState, InjectedState],
        topic: str,
        language: str = "中文",
        length: int = 100,
        # tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """该工具用于根据主题生成纯文本文案内容，不带图片标签和url
    Args:
        topic: 内容创作的主题

    Returns:
        最络内容分析报告 json格式
    """

    logger.info(f"topic={topic}")
    # Build prompt
    CONTENT_GENERATE_PROMPT = SIMPLE_TXT_CONTENT_GENERATE_SUB_AGENT_INSTRUCTIONS.format(
        length=length,
        topic=topic,
        language=language,

    )
    logger.info(f"pure CONTENT_GENERATE_PROMPT=============>:{CONTENT_GENERATE_PROMPT}")
    messages = [
        {
            "role": "user",
            "content": CONTENT_GENERATE_PROMPT,

        }

    ]
    content_generated = pure_content_generate_agent.invoke({
        "messages": messages,
    },)
    # Define the API endpoint URL
    logger.info(f"pure text content_generated=============>:{content_generated}")

    return content_generated



@tool
def batch_wash_docs(
        state: Annotated[DeepAgentState, InjectedState],
        origin_content: str,
        polish_prompt: str="暂无要求",
        batch_size: int = 5,
        # tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """文档洗稿工具, 根据洗稿前的一份原始文本(origin_content) 一次批量生成多份(batch_size)修饰润色文案内容，
    Args:
        origin_content: 洗稿原始文本
        batch_size: 批量生成文档的数量,
    Returns:
        最络内容分析报告 json格式
    """

    logger.info(f"**** state--->{state}")
    # attachments = state.get("attachments", [])
    # attachment_content=None
    # if attachments:
    #     chunks: list[str] = []
    #     for idx, attachment in enumerate(attachments, 1):
    #         logger.info(f"attachment file_name--->{attachment["file_name"]}")
    #         attachment_content=attachment["markdown"]
    #         logger.info(f"attachment file_content--->{attachment_content}")

    logger.info(f"origin_content={origin_content}, batch_size={batch_size}   polish_prompt:{polish_prompt}")
    url = "http://8.137.51.150:9999/AI/multi_channel_chat"
    content_generated='abcd1234'
    if origin_content is not None:
       payload = {
           "content": origin_content+" polish_prompt:"+polish_prompt,
           "thread_count": batch_size,
           "type": "messages",
           "from": 3
       }
       api_key="5abd458a2a06c6bba31eac7bed31c621"
       headers = {"X-Auth-Token": f"{api_key}",
                  "Content-Type": "application/json",
                  "accept": "text/event-stream"}
       content_chunks={}
       with requests.post(url, json=payload, headers=headers, stream=True) as r:
           for line in r.iter_lines(decode_unicode=True):
               # logger.info(f"------------> :{line}")
               if line.startswith('data:'):
                   data = line[5:].strip()
                   json_data = json.loads(data)
                   # logger.info(f"json_data index--->: {json_data["index"]}  data:{json_data["data"]}")
                   if content_chunks.get(json_data["index"]) is None:
                       content_chunks[json_data["index"]]=json_data["data"]
                   else:
                       content_chunks[json_data["index"]] += json_data["data"]



    # logger.info(f"content_generated=============>:{content_chunks}")
    file_links=[]
    file_prefix=""
    for index,current_content in content_chunks.items():
        logger.info(f"index:{index}")
        logger.info(f"current_content:{current_content}")
        index_of_chat_id = current_content.find("chat_rec_id")
        if index_of_chat_id > 0 :
            chat_rec_id=current_content[index_of_chat_id+len("chat_rec_id")+3:-2]
            logger.info(f"-----> chat_rec_id:{chat_rec_id}")
        with open(f"/Volumes/vol_lxy_export/export/tmp/generated_file_{chat_rec_id}.md", "w") as md_file:
            md_file.write(current_content)
            md_file.flush()
            md_file.close()

        logger.info(f"/Volumes/vol_lxy_export/export/tmp/generated_file_{chat_rec_id}.md  created successfully!")
        file_links.append({"file_name":f"generated_file_{chat_rec_id}.md",
                           "content":f"{current_content}" })
    # logger.info(f"length of content_generated=============>:{len(content_chunks)}")

    return file_links



