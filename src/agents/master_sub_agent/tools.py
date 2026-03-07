"""Master-Sub Agent 工具定义

从 multi_task_agent 复制的工具定义
"""

import re
from typing import Literal

from langchain_core.tools import tool


# ==================== 邮件工具 ====================

@tool
def validate_email_address(email: str) -> dict[str, bool | str]:
    """验证邮箱地址的合法性

    Args:
        email: 待验证的邮箱地址

    Returns:
        包含验证结果的字典
    """
    if not email:
        return {"valid": False, "error": "邮箱地址不能为空"}

    # 简单的邮箱格式验证
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return {"valid": False, "error": "邮箱地址格式不正确"}

    return {"valid": True, "error": ""}


@tool
def send_email(mail_address: str, mail_topic: str, mail_content: str) -> str:
    """发送邮件（模拟）

    Args:
        mail_address: 收件人邮箱
        mail_topic: 邮件主题
        mail_content: 邮件内容

    Returns:
        发送结果
    """
    # 这里是模拟发送，实际项目中应该调用真实的邮件发送接口
    return f"邮件已成功发送到 {mail_address}，主题：{mail_topic}，内容：{mail_content}"


# ==================== 图片生成工具 ====================

@tool
def validate_image_params(description: str, style: str, width: int, height: int, count: int) -> dict[str, bool | list[str]]:
    """验证图片生成参数

    Args:
        description: 图片描述
        style: 图片风格
        width: 图片宽度
        height: 图片高度
        count: 图片数量

    Returns:
        包含验证结果的字典
    """
    errors = []

    if not description:
        errors.append("图片描述不能为空")

    if not style:
        errors.append("图片风格不能为空")

    if width <= 0 or width > 4096:
        errors.append("图片宽度必须在 1-4096 之间")

    if height <= 0 or height > 4096:
        errors.append("图片高度必须在 1-4096 之间")

    if count <= 0 or count > 10:
        errors.append("图片数量必须在 1-10 之间")

    return {"valid": len(errors) == 0, "errors": errors}


@tool
def generate_image(description: str, style: str, width: int, height: int, count: int) -> str:
    """生成图片（模拟）

    Args:
        description: 图片描述
        style: 图片风格
        width: 图片宽度
        height: 图片高度
        count: 图片数量

    Returns:
        生成结果
    """
    # 这里是模拟生成，实际项目中应该调用真实的图片生成接口
    return f"已生成 {count} 张图片（风格：{style}，尺寸：{width}x{height}，描述：{description}）"


# ==================== TTS 工具 ====================

@tool
def validate_tts_params(tts_content: str, voice_sample_url: str = "") -> dict[str, bool | list[str]]:
    """验证 TTS 参数

    Args:
        tts_content: 语音文案
        voice_sample_url: 语音样本文件URL（可选）

    Returns:
        包含验证结果的字典
    """
    errors = []

    if not tts_content:
        errors.append("语音文案不能为空")

    return {"valid": len(errors) == 0, "errors": errors}


@tool
def generate_tts(tts_content: str, voice_sample_url: str = "") -> str:
    """生成 TTS 语音（模拟）

    Args:
        tts_content: 语音文案
        voice_sample_url: 语音样本文件URL（可选，不提供则使用默认语音）

    Returns:
        生成结果
    """
    # 这里是模拟生成，实际项目中应该调用真实的 TTS 接口
    voice_info = f"使用自定义语音样本 ({voice_sample_url})" if voice_sample_url else "使用默认语音"
    return f"已生成 TTS 语音，{voice_info}，文案：{tts_content}"


# ==================== 天气查询工具 ====================

@tool
def query_weather(city: str) -> str:
    """查询天气（模拟）

    Args:
        city: 城市名

    Returns:
        天气信息
    """
    # 这里是模拟查询，实际项目中应该调用真实的天气查询接口
    return f"{city} 今天天气：晴，温度 18-28°C，空气质量优"


# ==================== 数字人工具 ====================

@tool
def validate_digital_human_params(digital_image: str, digital_content: str) -> dict[str, bool | list[str]]:
    """验证数字人参数

    Args:
        digital_image: 数字人图片
        digital_content: 数字人口播文稿

    Returns:
        包含验证结果的字典
    """
    errors = []

    if not digital_image:
        errors.append("数字人图片不能为空")

    if not digital_content:
        errors.append("数字人口播文稿不能为空")

    return {"valid": len(errors) == 0, "errors": errors}


@tool
def create_digital_human(digital_image: str, digital_content: str, digital_sample: str = "") -> str:
    """创建数字人视频（模拟）

    Args:
        digital_image: 数字人图片
        digital_content: 数字人口播文稿
        digital_sample: 数字人口播声音样本（可选）

    Returns:
        生成结果
    """
    # 这里是模拟生成，实际项目中应该调用真实的数字人生成接口
    sample_info = f"使用自定义声音样本 ({digital_sample})" if digital_sample else "使用默认声音"
    return f"已创建数字人视频，{sample_info}，文稿：{digital_content}"


# ==================== 各子智能体工具集 ====================

def get_mail_agent_tools() -> list:
    """获取邮件子智能体的工具集"""
    return [
        validate_email_address,
        send_email,
    ]


def get_image_agent_tools() -> list:
    """获取图片生成子智能体的工具集"""
    return [
        validate_image_params,
        generate_image,
    ]


def get_tts_agent_tools() -> list:
    """获取 TTS 子智能体的工具集"""
    return [
        validate_tts_params,
        generate_tts,
    ]


def get_weather_agent_tools() -> list:
    """获取天气查询子智能体的工具集"""
    return [
        query_weather,
    ]


def get_digital_human_agent_tools() -> list:
    """获取数字人子智能体的工具集"""
    return [
        validate_digital_human_params,
        create_digital_human,
    ]


# ==================== 获取所有工具 ====================

def get_master_sub_tools() -> list:
    """获取主控+子智能体系统的所有工具（保留用于主控智能体）"""
    return [
        validate_email_address,
        send_email,
        validate_image_params,
        generate_image,
        validate_tts_params,
        generate_tts,
        query_weather,
        validate_digital_human_params,
        create_digital_human,
    ]
