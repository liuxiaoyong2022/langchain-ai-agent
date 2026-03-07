"""Multi-Task Agent 状态定义"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated, Literal

from langchain.messages import AnyMessage
from langgraph.graph import add_messages

from src.agents.common.state import BaseState


@dataclass
class TaskState:
    """单个任务的状态"""
    task_type: str = ""  # 任务类型：mail, image, tts, weather, digital_human
    task_data: dict = field(default_factory=dict)  # 任务数据
    is_validated: bool = False  # 是否已校验
    is_confirmed: bool = False  # 是否已用户确认
    validation_errors: list[str] = field(default_factory=list)  # 校验错误信息


@dataclass
class MultiTaskState(BaseState):
    """多任务智能体的状态"""

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)

    # 任务管理
    current_task: TaskState | None = None  # 当前任务
    completed_tasks: list[TaskState] = field(default_factory=list)  # 已完成的任务
    pending_tasks: list[TaskState] = field(default_factory=list)  # 待处理的任务

    # 对话状态
    awaiting_user_confirmation: bool = False  # 是否等待用户确认
    intent: str = ""  # 识别到的意图：mail, image, tts, weather, digital_human, unknown

    # 收集的信息
    collected_info: dict = field(default_factory=dict)  # 已收集的信息

    # 结果
    task_result: str = ""  # 任务执行结果


@dataclass
class MailTaskData:
    """邮件任务数据"""
    mail_address: str = ""
    mail_topic: str = ""
    mail_content: str = ""


@dataclass
class ImageTaskData:
    """图片生成任务数据"""
    description: str = ""
    style: str = "写实"
    width: int = 1024
    height: int = 768
    count: int = 1


@dataclass
class TTSTaskData:
    """TTS任务数据"""
    tts_content: str = ""
    voice_sample_url: str = ""  # 可选，默认使用默认语音


@dataclass
class WeatherTaskData:
    """天气查询任务数据"""
    city: str = ""


@dataclass
class DigitalHumanTaskData:
    """数字人任务数据"""
    digital_image: str = ""
    digital_content: str = ""
    digital_sample: str = ""  # 可选，声音样本
