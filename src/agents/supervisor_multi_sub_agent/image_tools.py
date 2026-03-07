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

from datetime import datetime
from typing import Dict, Any, List, Optional


collection_state = {
            "description": None,
            "style": None,
            "width": 1024,
            "height": 768,
            "count": 1
}
@tool
def generate_image(description: str, style: str, width: int, height: int, count: int) -> str:
# def generate_image(description: str, style: str = "写实", width: int = 1024, height: int = 768, count: int = 1) -> str:
        """
        生成图片

        Args:
            description: 图片描述
            style: 图片风格
            width: 图片宽度
            height: 图片高度
            count: 生成数量

        Returns:
            生成结果信息
        """
        # 这里应该调用实际的图片生成API（如DALL-E、Stable Diffusion等）
        # 为了演示，返回模拟结果
        # format_str="YYYY-MM-DD HH:MM:SS"
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

        print("iamge_gen 当前时间：", formatted_time)
        # 格式化输出
        timestamp = now.strftime(formatted_time)
        # timestamp = datetime.time().strftime("%Y%m%d_%H%M%S")
        results = []
        print(f"step 2.0 do mock generate_image----------->description:{description}    style:{style} width:{width}  height:{height}  count:{count}")
        mock_image_time=10
        sleep(mock_image_time)
        print(f"step 2.0.5 ----------->do mock generate_image finished  after mock_image_time:{mock_image_time} second")

        for i in range(count):
            result = {
                "id": f"img_{formatted_time}_{i+1}",
                "description": description,
                "style": style,
                "size": f"{width}x{height}",
                "status": "生成成功",
                "url": f"/outputs/image_{formatted_time}_{i+1}.png"
            }
            results.append(result)
        print(f"step 2.1.1 do mock generate_image finished -----------> results:{results}  ")
        return json.dumps({
            "success": True,
            "message": f"成功生成 {count} 张图片",
            "images": results
        }, ensure_ascii=False)

# @tool
# def start_parameter_collection( user_input: str) -> Dict[str, Any]:
#         """
#         开始参数收集流程
#         返回: {"need_input": bool, "message": str, "complete": bool}
#         """
#         # self.collecting_params = True
#         # self.current_step = 0
#         # self.collection_history = []
#         # self.collection_state = {
#         #     "description": None,
#         #     "style": None,
#         #     "width": 1024,
#         #     "height": 768,
#         #     "count": 1
#         # }
#
#         print(f"step 1.9.0 start_parameter_collection---------->user_input:{user_input}")
#         # 尝试从用户输入中提取初始信息
#         initial_info = _extract_initial_info(user_input)
#         print(f"step 1.9.1 start_parameter_collection---------->initial_info:{initial_info}")
#         # return initial_info
#         return _next_collection_step(initial_info)

def continue_collection(self, user_input: str) -> Dict[str, Any]:
        """
        继续参数收集流程
        """
        if not self.collecting_params:
            return {"error": "不在参数收集模式中"}

        self.collection_history.append(user_input)
        return self._next_collection_step(user_input)


def _extract_initial_info( user_input: str) -> Dict[str, Any]:
    """从初始输入中提取信息"""
    info = {}

    # 简单的关键词提取（在实际项目中可以使用更复杂的NLP）
    input_lower = user_input.lower()

    # 尝试提取图片描述
    if "生成" in user_input or "图片" in user_input or "图像" in user_input:
        # 移除常见的指令词
        desc = user_input.replace("生成", "").replace("图片", "").replace("图像", "")
        desc = desc.replace("一张", "").replace("一个", "").strip()
        if desc:
            info["description"] = desc

    # 尝试提取风格
    styles = ["卡通", "写实", "抽象", "油画", "水彩", "素描", "动漫", "3D", "赛博朋克", "极简"]
    for style in styles:
        if style in user_input:
            info["style"] = style
            break

    # 尝试提取数量
    if "张" in user_input or "个" in user_input:
        import re
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            info["count"] = min(int(numbers[0]), 10)  # 限制最多10张

    # 尝试提取尺寸
    if "1920" in user_input or "1080" in user_input:
        info["width"] = 1920
        info["height"] = 1080

    return info


def _next_collection_step( current_input: str = "") -> Dict[str, Any]:
    """
    执行下一步参数收集
    """
    steps = [
        ("description", "请描述您想要生成的图片内容："),
        ("style", "请选择图片风格（例如：卡通、写实、油画、水彩、素描、动漫、3D、赛博朋克、极简等）："),
        ("size", "请输入图片尺寸（默认：1024*768，您也可以输入如 1920*1080）："),
        ("count", "请输入需要生成的图片数量（1-10张，默认1张）：")
    ]

    # 更新已收集的信息
    # if current_input:
    #     _update_collection_state(current_input)

    # 找到下一个需要收集的参数
    for i, (param, prompt) in enumerate(steps):
        value = collection_state[param]
        print(f"step 1.9.2 _next_collection_step---------->value:{value}   param:{param}   prompt:{prompt}")
        # 跳过已有值且已确认的参数
        if value is not None and param != "size":  # size特殊处理
            continue

        # 处理尺寸特殊逻辑
        if param == "size" and collection_state["width"] == 1024 and collection_state["height"] == 768:
            # 使用默认值，跳过
            continue

        if value is None:
            current_step = i
            need_input={
                "need_input": True,
                "message": f"[{i + 1}/4] " + prompt,
                "complete": False,
                "current_state": collection_state.copy()
            }
            print(f"step 1.9.3 _next_collection_step---------->need_input:{need_input}")

            return need_input


    # 所有参数都收集完成
    need_input = {
        "need_input": False,
        "message": "参数收集完成！准备生成图片...",
        "complete": True,
        "current_state": collection_state.copy()
    }
    print(f"step 1.9.4 _next_collection_step---------->need_input:{need_input}")
    return need_input

# def _update_collection_state( user_input: str):
#         """更新收集状态"""
#         current_step = self.current_step
#         steps = ["description", "style", "size", "count"]
#
#         if current_step >= len(steps):
#             return
#
#         param = steps[current_step]
#
#         if param == "description":
#             self.collection_state["description"] = user_input.strip()
#
#         elif param == "style":
#             self.collection_state["style"] = user_input.strip()
#
#         elif param == "size":
#             # 解析尺寸
#             if "*" in user_input or "x" in user_input.lower():
#                 import re
#                 numbers = re.findall(r'\d+', user_input)
#                 if len(numbers) >= 2:
#                     self.collection_state["width"] = int(numbers[0])
#                     self.collection_state["height"] = int(numbers[1])
#             elif "默认" in user_input or user_input.strip() == "":
#                 pass  # 使用默认值
#
#         elif param == "count":
#             import re
#             numbers = re.findall(r'\d+', user_input)
#             if numbers:
#                 count = max(1, min(int(numbers[0]), 10))
#                 self.collection_state["count"] = count
