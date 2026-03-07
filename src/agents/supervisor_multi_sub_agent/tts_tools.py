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
from src.utils import logger
COMFY_UI_URL = os.getenv("COMFY_UI_URL")
COMFY_UI_TASK_URL = os.getenv("COMFY_UI_TASK_URL")
LOCAL_IMAGE_GEN_API_KEY = os.getenv('LOCAL_IMAGE_GEN_API_KEY')
import json
# from src.claude_code.download_file import download_file
# from src.claude_code.upload_file import upload_file
from time import sleep
from urllib.parse import urlparse

from src.agents.common import BaseAgent, load_chat_model
from src import config
from datetime import datetime
from time import sleep


# @tool()
# def tts_txt_to_audio_with_sample_tool(
#         content:str,
#         voice_motion:str="",
#         voice_sample_url:str=None
#
# ) -> str:
#     """本工具用于把文本信息和语音样本转换为语音或语频文件
#     Args:
#         content: 用来转换为语音的文本信息
#         tool_call_id: Injected tool call identifier for message tracking
#         voice_motion: 声音中带有的情感参数包括 happy, angry, sad, afraid, disgusted, melancholic, surprised ,calm 这些纬度 取值在 0~1 之间
#         voice_sample_url: 语音样本文件url
#     # Returns:
#     #     Formatted string representation of the current read kb
#     """
#
#     logger.info(f"***=========>do tts_txt_to_audio_tool content:{content} ,  voice_sample_url:{voice_sample_url},   voice_motion:{voice_motion}  ")
#     # 这里需要检查voice_sample_url 声音样本的来源，如果是  http:// 或是 http://
#     # Define the API endpoint URL
#     comfyui_url = f'{COMFY_UI_URL}'
#     save_path = os.getenv("DOWN_LOAD_TMP_PATH")
#     voice_sample_url = check_and_download_and_upload(voice_sample_url,save_path)
#     logger.info(f"---->checked voice_sample_url:{voice_sample_url} ")
#
#     input_dic= voice_motion
#     default_dic="{\"happy\":0.2,\"angry\":0.3,\"sad\":0,\"afraid\":0,\"disgusted\":0,\"melancholic\":0,\"surprised\":0,\"calm\":0}"
#     payload = {
#         "workflow_id": 10,
#         "params": {
#             "input_text":content.replace("\n"," "),
#             "input_dic": input_dic,
#             "internal_audio":voice_sample_url
#         }
#     }
#     headers = {"X-Auth-Token": f"{LOCAL_IMAGE_GEN_API_KEY}", "Content-Type": "application/json"}
#     logger.info(f"payload------------>{payload}")
#
#     #启动tts生成,获取任务id
#     task_id = -1
#     task_code = 0
#     with requests.post(comfyui_url, json=payload, headers=headers, stream=True) as r:
#         for line in r.iter_lines(decode_unicode=True):
#             logger.info(f"------------>  line:{line}")
#             json_data = json.loads(line)
#             logger.info(f"code ------------>  :{json_data["code"]}")
#             if json_data["code"] == 200:
#                 task_id = json_data["data"]["id"]
#                 logger.info(f"task_id ------------>  :{task_id}")
#
#                 # print(f"json_data--->: {json_data}")
#
#     comfyui_task_url = f'{COMFY_UI_TASK_URL}'
#
#     default_tts_audio_url = 'prompt_normal_man_temp-2.wav'
#     if task_id== -1:
#         #获取任务id 失败
#         logger.error(f"获取任务id 失败  task_id:{task_id }")
#         return default_tts_audio_url
#
#
#     comfyui_task_url = f'{COMFY_UI_TASK_URL}'
#     audio_file: str = None
#     subfolder:str = None
#     task_query_payload = {
#         "id": task_id,
#     }
#
#     loop_i = 0
#     while audio_file is None:
#         loop_i = loop_i + 1
#         logger.info(f"sleep loop_i ------------>:{loop_i}")
#         with requests.post(comfyui_task_url, json=task_query_payload, headers=headers, stream=True) as r:
#             for line in r.iter_lines(decode_unicode=True):
#                 logger.info(f"------------>  line:{line}")
#                 json_data = json.loads(line)
#                 if json_data["code"] == 200:
#                     task_id = json_data["data"]["id"]
#                     result_code = json_data["data"]["result_node"]
#                     logger.info(f"task_id ----->  :{task_id}   result_code:{result_code}")
#                     # yield f"***yield  task_id ------------>  :{task_id}"
#
#                     outputs = json_data["data"]["outputs"]
#                     logger.info(f"outputs ------------>  :{outputs}")
#                     if outputs is not None:
#                         audio_file = outputs[result_code]["audio"][0]["filename"]
#                         subfolder = outputs[result_code]["audio"][0]["subfolder"]
#                         logger.info(f"audio_file ------------>  :{audio_file}")
#
#         #轮询间隔5秒
#         sleep(5)
#
#     downlaod_url=f"https://carbotai.com/comfyui/view?filename={audio_file}&subfolder={subfolder}"
#
#     #这里将文件下载到本地临时目录
#     download_file(
#         url=downlaod_url,
#         save_path=save_path,
#         filename= audio_file,
#         chunk_size=16384,
#         timeout=60
#     )
#     #这里再将文件上传到comfyui
#     uplaod_url="https://carbotai.com/api/comfy-ui/upload_file"
#     file_upload_path=f"{save_path}/{audio_file}"
#     upload_result = upload_file(
#         url= uplaod_url,
#         file_path=file_upload_path,
#         headers={"X-Auth-Token": LOCAL_IMAGE_GEN_API_KEY}
#     )
#
#     logger.info(f"upload_result-------->{upload_result}")
#
#     logger.info(f"audio_file-------->{audio_file}")
#     return audio_file.strip()
#     # logger.info(f"tts_audio_url-------->{tts_audio_url}")
#     # return default_tts_audio_url
#


# def check_and_download_and_upload(file_path:str,save_path:str) -> str:

#     if  file_path.startswith("http") or file_path.startswith("https"):
#         parsed_url = urlparse(file_path)
#         filename = os.path.basename(parsed_url.path)
#         logger.info(f"get filename:{filename}   from {parsed_url}")
#         # 这里将文件下载到本地临时目录
#         download_file(
#             url=file_path,
#             save_path=save_path,
#             filename=filename,
#             chunk_size=16384,
#             timeout=60
#         )
#         # 这里将文件上传到comfyui 服务
#         # 这里再将文件上传到comfyui
#         uplaod_url = "https://carbotai.com/api/comfy-ui/upload_file"
#         file_upload_path = f"{save_path}/{filename}"
#         upload_result = upload_file(
#             url=uplaod_url,
#             file_path=file_upload_path,
#             headers={"X-Auth-Token": LOCAL_IMAGE_GEN_API_KEY}
#         )
#         upload_file_name =None
#         logger.info(f"upload_result-------->{upload_result}   filename:{filename}")

#         if upload_result["status_code"]==200:
#             response=upload_result["response"]
#             if response["code"] == 200:
#                 upload_file_name = response["data"]["name"]
#                 logger.info(f"***  get upload_file_name-------->{upload_file_name}   filename:{filename}")


#         if upload_file_name is not None:
#             return upload_file_name
#         else:
#             logger.error(f"***------> 上传文件没有返回 upload_file_name 只好返回 filename:{filename}")
#             return filename


#     else:
#         logger.info(f"Not start with http or https of filename:{file_path}")
#         return file_path


@tool
def text_to_speech(text: str, voice: str = "alloy", output_filename: str = None) -> str:
        """
           将文字转换为语音

           Args:
               text: 要转换的文本内容
               voice: 语音类型（alloy, echo, fable, onyx, nova, shimmer）
               output_filename: 输出文件名（可选，不指定则自动生成）

           Returns:
               生成结果信息
           """
        try:
            OUTPUT_DIR="./tts_output/"
            print(f" step 5.1.1 --------->text_to_speech  text:{text}  voice:{voice}")
            # 生成输出文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"speech_{timestamp}.mp3"

            output_path = os.path.join(OUTPUT_DIR, output_filename)

            tts_gen_mock_time=6
            sleep(tts_gen_mock_time)
            # client = TTSAgent._get_client()
            # response = client.audio.speech.create(
            #     model=config.TTS_MODEL,
            #     voice=voice,
            #     input=text
            # )

            # 调用Mock TTS Gen

            print(f" step 5.1.2 mock --------->text_to_speech  mock tts finished spend time {tts_gen_mock_time} second output_path:{output_path}")
            # # 保存音频文件
            # response.stream_to_file(output_path)

            return json.dumps({
                "success": True,
                "message": "语音生成成功",
                "output_file": output_path,
                "voice": voice,
                "text_length": len(text),
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"语音生成失败: {str(e)}",
                "text": text[:100] + "..." if len(text) > 100 else text
            }, ensure_ascii=False)


@tool
def generate_audio_script(topic: str, style: str = "对话", duration_minutes: int = 5) -> str:
        """
        生成音频脚本

        Args:
            topic: 音频主题
            style: 脚本风格（对话、演讲、故事、新闻等）
            duration_minutes: 预计时长（分钟）

        Returns:
            生成的脚本内容
        """
        try:
            # 使用LLM生成脚本
            # llm = TTSAgent._get_llm()
            print(f"step 5.3.1 generate_audio_script -----------> 请创建一个{style}风格的音频脚本，主题是{topic}，预计时长{duration_minutes}分钟 ")
            model = load_chat_model(config.default_model)
            prompt = f"""请创建一个{style}风格的音频脚本，主题是"{topic}"，预计时长{duration_minutes}分钟。

    要求：
    1. 内容流畅自然，适合口语表达
    2. 按照预计时长合理安排内容长度
    3. 标注适当的停顿和语气提示
    4. 结构清晰，有开头、主体和结尾

    请直接输出脚本内容。"""

            response = model.invoke(prompt)
            print(f"step 5.3.2 generate_audio_script -----------> response {response} ")
            return json.dumps({
                "success": True,
                "message": "脚本生成成功",
                "topic": topic,
                "style": style,
                "estimated_duration": f"{duration_minutes}分钟",
                "script": response.content
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"脚本生成失败: {str(e)}"
            }, ensure_ascii=False)



@tool
def batch_text_to_speech(texts: list, voice: str = "alloy") -> str:
        """
        批量将多个文本转换为语音

        Args:
            texts: 文本列表
            voice: 语音类型

        Returns:
            批量生成结果
        """
        try:
            # from config.settings import Config
            # config = Config()
            # client = TTSAgent._get_client()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results = []

            for i, text in enumerate(texts):
                try:
                    output_filename = f"batch_speech_{timestamp}_{i+1}.mp3"
                    output_path = os.path.join(config.OUTPUT_DIR, output_filename)

                    # response = client.audio.speech.create(
                    #     model=config.TTS_MODEL,
                    #     voice=voice,
                    #     input=text
                    # )
                    # response.stream_to_file(output_path)
                    tts_gen_mock_time=5
                    sleep(tts_gen_mock_time)
                    print(f"step 5.5 batch_text_to_speech -----------> mock gen tts finished spend {tts_gen_mock_time} second")



                    results.append({
                        "index": i + 1,
                        "success": True,
                        "output_file": output_path,
                        "text": text[:50] + "..." if len(text) > 50 else text
                    })

                except Exception as e:
                    results.append({
                        "index": i + 1,
                        "success": False,
                        "error": str(e),
                        "text": text[:50] + "..." if len(text) > 50 else text
                    })

            success_count = sum(1 for r in results if r["success"])

            return json.dumps({
                "success": True,
                "message": f"批量生成完成，成功 {success_count}/{len(texts)} 个",
                "voice": voice,
                "results": results
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"批量生成失败: {str(e)}"
            }, ensure_ascii=False)
