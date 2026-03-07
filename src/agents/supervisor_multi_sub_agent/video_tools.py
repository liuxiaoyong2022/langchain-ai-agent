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
import json
from time import sleep
from src.utils import logger
from langgraph.types import Command
COMFY_UI_URL = os.getenv("COMFY_UI_URL")
DIGITAL_HUMAN_FLOW_ID = os.getenv("DIGITAL_HUMAN_FLOW_ID")
COMFY_UI_TASK_URL = os.getenv("COMFY_UI_TASK_URL")
# from .tts_tools import check_and_download_and_upload
@tool()
def digital_human_video_gen_tool(
        tool_call_id: Annotated[str, InjectedToolCallId],
        audio_url:str,
        human_image_url:str="",
        video_prompt:str="一定要帅气"

) -> Command:
    """本工具用语音+图片生成数字人口播视频
    Args:
         audio_url: 语音文件对应的访问链接
        human_image_url: 用于生成数字人(digital_human)的图片
    # Returns:
    #     Formatted string representation of the current read kb
    """

    logger.info(f"***=========>do digital_human_video_gen_tool audio_url:{audio_url} ,  human_image_url:{human_image_url}, video_prompt:{video_prompt} ")
    # Define the API endpoint URL
    comfyui_url = f'{COMFY_UI_URL}'
    save_path = os.getenv("DOWN_LOAD_TMP_PATH")
    #这里需要检查数字人图片样本human_image_url
    human_image_url = check_and_download_and_upload(human_image_url, save_path)
    logger.info(f"---->checked human_image_url:{human_image_url} ")


    payload = {
        "workflow_id": 9,
        "params": {
            "input_text": video_prompt,
            "internal_image": human_image_url,
            "internal_audio": audio_url,

        }
    }
    headers = {"X-Auth-Token": f"{os.getenv('LOCAL_IMAGE_GEN_API_KEY')}", "Content-Type": "application/json"}
    digital_human_video_url="http://example/digital_human_mock_video.mp4"

    logger.info(f"payload:{payload}")
    task_id = -1
    task_code = 0
    # with requests.post(comfyui_url, json=payload, headers=headers, stream=True) as r:
    #     for line in r.iter_lines(decode_unicode=True):
    #         logger.info(f"------------>  line:{line}")
    #         json_data = json.loads(line)
    #         logger.info(f"code ------------>  :{json_data["code"]}")
    #         if json_data["code"] == 200:
    #             task_id = json_data["data"]["id"]
    #
    #             logger.info(f"task_id ------------>  :{task_id}")
    #
                # yield f"task_id ------------>  :{task_id}"

                # print(f"json_data--->: {json_data}")

    task_id = 11455401408

    if task_id == -1:
        # 获取任务id 失败
        logger.error(f"获取任务id 失败  task_id:{task_id}")
        return digital_human_video_url

    comfyui_task_url = f'{COMFY_UI_TASK_URL}'
    video_file: str = None
    subfolder: str = None
    tts_audio_url = 'http://ttsexample/normal-gen/abcd123.wav'
    task_query_payload = {
        "id": task_id,
    }

    loop_i = 0
    while video_file is None:
        loop_i = loop_i + 1
        logger.info(f"sleep loop_i ------------>:{loop_i}")
        with requests.post(comfyui_task_url, json=task_query_payload, headers=headers, stream=True) as r:
            for line in r.iter_lines(decode_unicode=True):
                logger.info(f"------------>  line:{line}")
                json_data = json.loads(line)
                if json_data["code"] == 200:
                    task_id = json_data["data"]["id"]
                    result_code = json_data["data"]["result_node"]
                    logger.info(f"task_id ----->  :{task_id}   result_code:{result_code}")
                    outputs = json_data["data"]["outputs"]
                    print(f"outputs ------------>  :{outputs}")
                    if outputs is not None:
                        video_file = outputs[result_code]["gifs"][0]["filename"]
                        subfolder = outputs[result_code]["gifs"][0]["subfolder"]
                        logger.info(f"video_file ------------>  :{video_file}     subfolder:{subfolder}")

        sleep(5)

    # result="http://example/digital_human_video_001.mp4"
    logger.info(f"------>   digital_human_video_url:{video_file}")
    #这里需要将最终生成的文件拼接成可访问url
    video_file_downlaod_url = f"https://carbotai.com/comfyui/view?filename={video_file}&subfolder={subfolder}"
    # return digital_human_video_url
    return video_file_downlaod_url
