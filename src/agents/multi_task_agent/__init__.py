"""Multi-Task Agent - 多任务协作智能体模块

基于 LangGraph 1.x 构建的多智能体协作系统，具备以下特性：
- 主控智能体进行意图识别和任务分发
- 任务规划智能体进行任务拆解
- 校验智能体进行参数校验
- 5个功能子智能体：邮件、图片生成、TTS、天气查询、数字人
- 支持多轮对话收集必要信息
- 用户确认机制确保操作安全
"""

from .context import MultiTaskContext
from .graph import MultiTaskAgent

__all__ = [
    "MultiTaskAgent",
    "MultiTaskContext",
]

# 模块元数据
__version__ = "1.0.0"
__author__ = "Yuxi-Know Team"
__description__ = "基于 LangGraph 1.x 的多任务协作智能体"
