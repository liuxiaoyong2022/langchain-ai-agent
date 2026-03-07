"""Master-Sub Agent - 主控+子智能体系统

基于 deep_agent 架构，使用 SubAgentMiddleware 实现主控智能体和多个子智能体协作
"""

from .context import MasterSubContext
from .graph import MasterSubAgent

__all__ = [
    "MasterSubAgent",
    "MasterSubContext",
]

# 模块元数据
__version__ = "1.0.0"
__author__ = "Yuxi-Know Team"
__description__ = "基于 SubAgentMiddleware 的主控+子智能体系统"
