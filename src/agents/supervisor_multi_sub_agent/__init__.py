"""Supervisor Agent - 任务规划及分配智能体模块

基于 deepagents 库构建的深度分析智能体，具备以下特性：
- 任务规划和分解能力
- 深度知识搜索和分析
- 子智能体协作
- 文件系统和长期记忆
- 综合分析和报告生成
"""

from .context import SupervisorContext
from .graph import SupervisorAgent

__all__ = [
    "SupervisorAgent",
    "SupervisorContext",
]

# 模块元数据
__version__ = "1.0.0"
__author__ = "lxy"
__description__ = "多子知能体(multi-sub-agent)协作 基于 create_deep_agent 的深度分析智能体"
