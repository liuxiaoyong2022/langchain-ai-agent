"""TODO management tools for task planning and progress tracking.

This module provides tools for creating and managing structured task lists
that enable agents to plan complex workflows and track progress through
multi-step operations.
"""
import requests
from typing import Annotated
import os
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from src.utils.logging_config import logger
from .prompts import CRITIQUE_INSTRUCTIONS
from .state import DeepAgentState, Todo
from fastapi import APIRouter, Depends, HTTPException, Query
# from .prompts import KB_INSTRUCTIONS
from src.utils import logger



@tool(description=CRITIQUE_INSTRUCTIONS)
def critique_tool_do_analyse_and_report(
        state: Annotated[DeepAgentState, InjectedState],
        query_result_processed:list ,
        tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """该工具用于对搜索结果的内容进行深入分析,并输出分析报告
    Args:
        state: Injected agent state for var storage
        query_result_processed: 从结果页面url提取出来的页面主要内容 列表,
    Returns:
        最络内容分析报告 json格式
    """

    # Define the API endpoint URL

    logger.info(f"============= query_result_processed length:len{query_result_processed}")
    logger.info(f"============= tool_call_id:{tool_call_id}")
    return "success"

# @tool(parse_docstring=True)
# def critique_tool_think_tool(reflection: str) -> str:
#     """Tool for strategic reflection on research progress and decision-making.
#
#     Use this tool after each search to analyze results and plan next steps systematically.
#     This creates a deliberate pause in the research workflow for quality decision-making.
#
#     When to use:
#     - After receiving search results: What key information did I find?
#     - Before deciding next steps: Do I have enough to answer comprehensively?
#     - When assessing research gaps: What specific information am I still missing?
#     - Before concluding research: Can I provide a complete answer now?
#     - How complex is the question: Have I reached the number of search limits?
#
#     Reflection should address:
#     1. Analysis of current findings - What concrete information have I gathered?
#     2. Gap assessment - What crucial information is still missing?
#     3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
#     4. Strategic decision - Should I continue searching or provide my answer?
#
#     Args:
#         reflection: Your detailed reflection on research progress, findings, gaps, and next steps
#
#     Returns:
#         Confirmation that reflection was recorded for decision-making
#     """
#     logger.info(f" do think_tool ============= {reflection}")
#     return f"Reflection recorded: {reflection}"
