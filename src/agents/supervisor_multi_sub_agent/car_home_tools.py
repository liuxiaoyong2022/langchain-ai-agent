from time import sleep
import uuid
from typing import Any
from playwright.sync_api import sync_playwright
import requests
from langgraph.prebuilt import InjectedState
import typing
from src.utils import logger
from langgraph.types import Command, interrupt
from langchain_core.tools import InjectedToolCallId, tool
import json
from .state import DeepAgentState
from typing import Annotated, Literal, NotRequired
from .file_tools import ls, read_file, write_file
from langchain_core.messages import ToolMessage
from datetime import datetime
import httpx
import uuid, base64
from markdownify import markdownify
import os
from pydantic import BaseModel, Field
from src.agents import agent_manager
from langchain.agents import create_agent
from src.agents.common import BaseAgent, load_chat_model
from readability import Document
from langchain_core.messages import HumanMessage
from .prompts import SUMMARIZE_WEB_SEARCH

# car_home_bbs_url = "https://sou.autohome.com.cn/luntan?q=&entry=44&error=0"
car_home_bbs_url = os.getenv("CAR_HOME_BBS_URL")
#文章搜索入口
# car_home_docs_url = "https://sou.autohome.com.cn/wenzhang?q=&entry=43&error=0"
car_home_docs_url = os.getenv("CAR_HOME_DOC_URL")


REMOVE_CSS_INSTRUCTIONS = "把传入内容中的html 和 css标签去掉 ,仅留下正文内容,并返回"
default_model="local-ollama/cnshenyang/qwen3-nothink:14b"
summarization_model=load_chat_model(default_model)
css_filter_agent = create_agent(
    model=summarization_model,
    tools = [],
    system_prompt=REMOVE_CSS_INSTRUCTIONS
)

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3947.100 Safari/537.36",
}
params = {
    # "follow_redirects": True,
    "allow_redirects": True
}
HTTPX_CLIENT = httpx.Client(timeout=30)  # Add 30 second timeout



@tool
def car_home_tool_doc_query(
              state: Annotated[DeepAgentState, InjectedState],
              keyword: str)-> list:
    """ 该工具用于汽车之家文章或文档查询
      Args:
        keyword: 查询关键字,用于汽车之家官网关于汽车行业发展动态以及车辆介绍文章的搜索
    """
    logger.info(f"****------>1 汽车之家 文章搜索 keyword: {keyword}" )
    query_result = do_query(car_home_docs_url,keyword)
    return query_result
    # processed_results = process_search_results(query_result)
    # return processed_results
    # Pause before sending; payload surfaces in result["__interrupt__"]

@tool
def car_home_tool_bbs_query(
        state: Annotated[DeepAgentState, InjectedState],
        keyword: str,
        tool_call_id: Annotated[str, InjectedToolCallId])-> list:
    """ 该工具用于汽车之家论坛查询
      Args:
        state: Injected agent state for var storage
        keyword: 查询关键字,用于汽车之家官网关于车辆各方面讨论以及使用评论信息的搜索
    """
    logger.info(f"****------>1 汽车之家 论坛搜索 keyword: {keyword}" )
    result = do_query(car_home_bbs_url,keyword)
    json_string = json.dumps(result)
    # processed_results = process_search_results(result)
    file_path="/tmp/bbs_query.json"
    # write_file(file_path=file_path,content=json_string)


    #将文件写到state中试试

    # logger.info(f"****------>2 汽车之家 论坛搜索 result lenth: {len(result)}  json_string--->:")

    return result
    # return processed_results

# @tool
# def extract_and_analyse_doc(
#         keyword: str,
#         search_results: list,
#         state: Annotated[DeepAgentState, InjectedState],
#         tool_call_id: Annotated[str, InjectedToolCallId]
#         # )-> str:
#        ) -> Command:
#     """  本工具用于评论或文章分析，通过参数接收评论或文章搜索的结果集query_result ，并从中的获取页面url,从而获取页面内容
#       Args:
#           keyword: 对应于search_results 的查询关键字,用于汽车之家官网 查询车辆各方面讨论以及使用评论信息
#           search_results:评论或文章搜索的结果集
#           state: 传入的agent状态对象,用于获取上下文信息
#           tool_call_id: Injected tool call identifier for message tracking
#
#     """
#
#     file_path="/tmp/bbs_query.json"
#     logger.info(f"****------>3 汽车之家 页面获取 query_result: {search_results}")
#
#     # # Process and summarize results
#     print(f"2   ------> extract_and_analyse_doc keyword:{keyword} ")
#     # processed_results = process_search_results(search_results)
#
#     # Save each result to a file and prepare summary
#     files = state.get("files", {})
#     saved_files = []
#     summaries = []
#     processed_results=[]
#     for i, result in enumerate(processed_results):
#         # Use the AI-generated filename from summarization
#         filename = result['filename']
#
#         # Create file content with full details
#         file_content = f"""# Search Result: {result['title']}
#
# **URL:** {result['url']}
# **Query:** {keyword}
# **Date:** {get_today_str()}
#
# ## Summary
# {result['summary']}
#
# ## Raw Content
# {result['raw_content'] if result['raw_content'] else 'No raw content available'}
# """
#
#         files[filename] = file_content
#         saved_files.append(filename)
#         summaries.append(f"- {filename}: {result['summary']}...")
#
#     # Create minimal summary for tool message - focus on what was collected
#     summary_text = f"""🔍 Found {len(processed_results)} result(s) for '{keyword}':
#
# {chr(10).join(summaries)}
#
# Files: {', '.join(saved_files)}
# 💡 Use read_file() to access full details when needed."""
#
#     return Command(
#         update={
#             "files": files,
#             "messages": [
#                 ToolMessage(summary_text, tool_call_id=tool_call_id)
#             ],
#         }
#     )

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")


@tool
def car_home_tool_process_search_results(results: list[dict]) -> list[dict]:
    """该工具主要用于从入参results列表中，提取出搜索结果 文档标题(doc_titile), 文档访问链接(doc_url),并通过
       doc_url访问 提取出文档主要内容 并返回
    Args:
        results: Tavily search results dictionary

    Returns:
        List of processed results with summaries
    """
    processed_results = []


    # Create a client for HTTP requests with timeout

    print(f"3 results length:--------->{len(results)}")
    for result in results :

        # Get url
        url = result['doc_url']
        print(f"4 current url :--------->{url}")
        # Read url with timeout and error handling
        try:
            print(f"index of http:{url.find("http://")}")
            if url.strip().find("http://") == 0:
                url = url.replace("http://", "https://")
            response = HTTPX_CLIENT.get(url, params=params, headers=headers, cookies=None)
            print(f"response: {response}")
            if response.status_code == 200:
                # Convert HTML to markdown
                # print(f"response code: {response.text}")
                html_content = response.text
                # 创建Document对象
                doc = Document(html_content)
                # 获取文章标题
                title = doc.title()
                # 获取文章正文
                try:
                    content = doc.summary()
                    content = content.replace("\xa0", " ")
                    print(f"标题: {title}")
                    print(f"step 1 正文---------->{content}")
                    ai_filter_content = css_filter_agent.invoke(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": content,
                                }
                            ],
                        }
                    )
                    ai_clean_content = str(ai_filter_content["messages"][-1])
                    # print(f"step 2 ai_clean_content----->:{ai_clean_content}")
                    if ai_clean_content.index("additional_kwargs") > 0:
                        ai_clean_content = ai_clean_content[0:ai_clean_content.index("additional_kwargs")]
                        print(f"step 3 fainal extracted content------->: {ai_clean_content}")  # Output: freeC
                    else:
                        continue
                    # summary_obj = summarize_webpage_content(ai_clean_content)
                    # print(f"step 4 summary ----->{summary_obj}")
                    raw_content = ai_clean_content
                except Exception as e:
                    # 捕获其他所有运行时异常
                    print(f"--->发生未知错误: {e}")
                    continue
            else:
                # Use Tavily's generated summary
                # raw_content = result.get('raw_content', '')
                summary_obj = Summary(
                    filename="URL_error.md",
                    summary=f'Error reading URL:{url}; try another search.'
                )
        except (httpx.TimeoutException, httpx.RequestError) as e:
            # Handle timeout or connection errors gracefully
            # raw_content = result.get('raw_content', '')
            summary_obj = Summary(
                filename="connection_error.md",
                summary= f'Could not fetch URL:{url} (timeout/connection error). Try another search.'
            )

        # uniquify file names
        # uid = base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b"=").decode("ascii")[:8]
        # name, ext = os.path.splitext(summary_obj.filename)
        # summary_obj.filename = f"{name}_{uid}{ext}"

        processed_results.append({
            'url': result['doc_url'],
            'title': result['doc_title'],
            # 'summary': summary_obj.summary,
            # 'filename': summary_obj.filename,
            'raw_content': raw_content,
        })

    return processed_results



def get_carhome_tools() -> list[Any]:
    """获取sendmail工具列表"""
    return [car_home_tool_doc_query,
            car_home_tool_bbs_query,
            car_home_tool_process_search_results]
    # return [doc_query,bbs_query,extract_and_analyse_doc]

class Summary(BaseModel):
    """Schema for webpage content summarization."""
    filename: str = Field(description="Name of the file to store.")
    summary: str = Field(description="Key learnings from the webpage.")


# def summarize_webpage_content(webpage_content: str) -> Summary:
#     """Summarize webpage content using the configured summarization model.
#
#     Args:
#         webpage_content: Raw webpage content to summarize
#
#     Returns:
#         Summary object with filename and summary
#     """
#     try:
#         # Set up structured output model for summarization
#         structured_model = summarization_model.with_structured_output(Summary)
#
#         # Generate summary
#         summary_and_filename = structured_model.invoke([
#             HumanMessage(content=SUMMARIZE_WEB_SEARCH.format(
#                 webpage_content=webpage_content,
#                 date=get_today_str()
#             ))
#         ])
#
#         return summary_and_filename
#
#     except Exception:
#         # Return a basic summary object on failure
#         return Summary(
#             filename="search_result.md",
#             summary=webpage_content[:1000] + "..." if len(webpage_content) > 1000 else webpage_content
#         )
#


def extract_element(elements: typing.List["ElementHandle"], page: int) -> list:
    print(f"当前第:{page}页------->找到{len(elements)}个搜索结果   ")
    page_result = []
    for element in elements:
        # test_title = element.query_selector('a[class="relative pr-25px truncate text-3b5998 underline hover:text-d60000 hover:no-underline visited:text-800080 "]').get_attribute("aria-label")
        # test_link =  element.query_selector('a[class="relative pr-25px truncate text-3b5998 underline hover:text-d60000 hover:no-underline visited:text-800080 "]').get_attribute("href")
        doc_title = element.query_selector('a').get_attribute("aria-label").replace("<em>","").replace("</em>","")
        doc_url = element.query_selector('a').get_attribute("href")
        # view_count = element.get_by('p[class="leading-20px pr-15px text-008000"]')
        print("标题:" + doc_title)
        print("链接:" + doc_url)

        page_result.append({
            "doc_title": doc_title,
            "doc_url": doc_url
        })
#     返回该页结果
    return page_result

def do_query(query_url: str, keyword: str) -> []:
    with sync_playwright() as p:
        all_result_list = []
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # page.goto('https://www.dongchedi.com')
        page.goto(query_url)
        page.wait_for_load_state('networkidle')

        # 找到搜索输入框，输入“特斯拉”
        search_input = page.query_selector(
            'input[class="search_input_section"]')
        search_input.fill(keyword)
        sleep(6)
        # 模拟回车键，进行搜索
        search_input.press('Enter')
        # page.wait_for_event('load')

        # 当前页获取搜索结果
        page.wait_for_load_state('networkidle')
        elements = page.query_selector_all('dt[class="flex items-center text-16px leading-26px"]')
        first_page_result = extract_element(elements, 0)
        all_result_list.extend(first_page_result)
        # print(f"------->找到{len(elements)}个搜索结果")
        # for element in elements:
        #     test_title = element.query_selector('a').get_attribute("aria-label").replace("<em>","").replace("</em>","")
        #     test_link = element.query_selector('a').get_attribute("href")
        #     # view_count = element.get_by('p[class="leading-20px pr-15px text-008000"]')
        #     print("标题:" + test_title)
        #     print("链接:" + test_link)
        #
        #
        #     print("==========================")
        #     # print(element.text_content())

        # 翻三页试试
        result=[];
        for i in range(1, 1):
        # for i in range(1, 2):
            # 找到分页组件下一页安钮,且点击
            page.query_selector('button[class="next cursor-pointer "]').click()
            page.wait_for_load_state('networkidle')
            elements = page.query_selector_all('dt[class="flex items-center text-16px leading-26px"]')
            # extract_element(elements, i)
            # result.append(elements)
            current_page_result = extract_element(elements, i)
            all_result_list.extend(current_page_result)
            sleep(5)  # 等待内容加载完成

        browser.close()
        #数据写到文件中


        return all_result_list


# @tool
# def sale_order()-> str:
#     """
#     该tool查询懂车帝官网 当前最国内汽内销售排名
#
#     """
#     logger.info("----> 懂车帝当前最国内汽内销售排名")
#     return "懂车帝当前最国内汽内销售排名"
