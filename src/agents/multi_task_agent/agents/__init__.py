"""Multi-Task Agent 子智能体模块

包含各个功能子智能体的实现
"""

from .mail_agent import create_mail_agent_node
from .image_agent import create_image_agent_node
from .tts_agent import create_tts_agent_node
from .weather_agent import create_weather_agent_node
from .digital_human_agent import create_digital_human_agent_node

__all__ = [
    "create_mail_agent_node",
    "create_image_agent_node",
    "create_tts_agent_node",
    "create_weather_agent_node",
    "create_digital_human_agent_node",
]
