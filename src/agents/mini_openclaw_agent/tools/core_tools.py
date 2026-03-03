"""
Mini-OpenClaw 核心工具实现
5个基础工具：Terminal, Python REPL, Fetch URL, Read File, RAG Search
"""
# import asyncio
import inspect
from typing import List
from pathlib import Path
import re
from langchain_community.tools import ShellTool
import requests
from bs4 import BeautifulSoup
import html2text
import subprocess
from langchain_experimental.tools import PythonREPLTool
from langchain_core.tools import tool
from typing import Optional
import os
from io import StringIO
import traceback
import signal
from contextlib import redirect_stdout, redirect_stderr
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from src.agents.mini_openclaw_agent.setting import get_settings
settings = get_settings()

class TimeoutException(Exception):
    """Exception raised when code execution times out."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutException("Code execution timed out")


class SecurePythonREPL:
    """A secure Python REPL with timeout and resource limits."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.locals = {}
        self.globals = {}

    def run(self, code: str, timeout: Optional[int] = None) -> str:
        """
        Execute Python code with timeout protection.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds (overrides default)

        Returns:
            Output from execution or error message
        """
        print(f"step 2.1 ------------>SecurePythonREPL code:{code} ")
        timeout = timeout or self.timeout

        # Set signal handler for timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)

        try:
            signal.alarm(timeout)

            output = StringIO()
            error = StringIO()

            with redirect_stdout(output), redirect_stderr(error):
                exec(code, self.globals, self.locals)

            result = output.getvalue()
            if result:
                return result
            else:
                return "Code executed successfully (no output)"

        except TimeoutException:
            return f"Error: Code execution timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {traceback.format_exc()}"
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

# 创建全局 REPL 实例
# _repl_instance = SecurePythonREPL(timeout=30)

class CustomPythonREPLTool(PythonREPLTool):
    """Custom Python REPL tool"""
    name: str = "python_repl"
    description: str = """
    Execute Python code in a REPL environment.
    Use this for calculations, data processing, and script execution.
    Input should be valid Python code.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

_repl_instance = CustomPythonREPLTool()


class RAGRetrievalTool(BaseTool):
    """RAG-based knowledge retrieval tool using LlamaIndex"""
    name: str = "search_knowledge_base"
    description: str = """
    Search the knowledge base for relevant information.
    Use this when the user asks about specific knowledge or documentation.
    Input should be a search query string.
    """
    index_dir: Path = Field(default_factory=lambda: Path(settings.storage_dir) / "rag_index", description="Directory to store RAG index")

    class Inputs(BaseModel):
        query: str = Field(description="Search query for the knowledge base")

    args_schema: Type[BaseModel] = Inputs

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._index = None
        self._query_engine = None

    def _build_index(self):
        """Build or load the RAG index"""
        try:
            from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
            from llama_index.core.node_parser import SentenceSplitter
            from langchain_openai import OpenAIEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            # from llama_index.embeddings.openai import OpenAIEmbedding
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)

            # Initialize embedding model
            # embedding_model = OpenAIEmbeddings()
            # embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)

            # Check if index exists
            index_path = self.index_dir / "index"
            if index_path.exists():
                # Load existing index
                print(f"step 4.0.3 ---------> Loading existing RAG index from {index_path}")
                from llama_index.core import StorageContext, load_index_from_storage
                storage_context = StorageContext.from_defaults(str(index_path))
                self._index = load_index_from_storage(storage_context)
            else:
                # Build new index
                if not settings.knowledge_dir.exists():
                    print(f"step 4.0.4 ---------> Knowledge directory does not exist: {settings.knowledge_dir}")
                    return False

                documents = SimpleDirectoryReader(
                    str(settings.knowledge_dir)
                ).load_data()

                splitter = SentenceSplitter(
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap
                )

                self._index = VectorStoreIndex.from_documents(
                    documents,
                    transform=splitter,
                    embed_model=embed_model
                )

                # Persist index
                self._index.storage_context.persist(str(index_path))

            # Create query engine
            self._query_engine = self._index.as_query_engine(
                similarity_top_k=settings.top_k,
                streaming=False
            )

            return True

        except Exception as e:
            print(f"Error building RAG index: {e}")
            return False

    def _run(self, query: str) -> str:
        """Search knowledge base"""

        print(f"step 4.0.2--------------> tool call search_knowledge_base query:{query} ")
        try:
            # Lazy initialization
            if self._query_engine is None:
                success = self._build_index()
                if not success:
                    return "Error: Knowledge base not available or empty"

            # Perform search
            response = self._query_engine.query(query)
            print(f"step 4.0.3--------------> tool call search_knowledge_base response:{response} ")
            # Format results
            results = f"Search Query: {query}\n\n"
            results += f"Answer: {str(response)}\n\n"

            # Add source information
            if hasattr(response, 'source_nodes'):
                results += "Sources:\n"
                for i, node in enumerate(response.source_nodes, 1):
                    source_info = node.metadata.get('file_name', 'Unknown')
                    results += f"{i}. {source_info}\n"

            return results

        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

_rag_retrieval_instance = RAGRetrievalTool()


@tool
def fetch_url(url: str) -> str:
    """
    Fetch content from a URL and return it as clean Markdown text.
    Use this to retrieve information from websites, APIs, or online resources.
    The HTML is automatically cleaned and converted to readable format.

    Args:
        url: The URL to fetch

    Returns:
        Cleaned Markdown content
    """
    print(f"step 1.5.0 -------------------> Fetching {url}")
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; Mini-OpenClaw/1.0)'}
        )
        response.raise_for_status()
        print(f"step 1.5.1 -------------------> Fetching response.content length:{len(response.content)}")
        # 清洗HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()

        # 转换为Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        markdown_content = h.handle(str(soup))

        # 限制长度（防止Token爆炸）
        if len(markdown_content) > 20000:
            markdown_content = markdown_content[:20000] + "\n\n...[truncated]"


        print(f"step 1.5.2 -------------------> Fetching markdown_content length:{len(markdown_content)}")
        return markdown_content

    except Exception as e:
        return f"Error fetching URL: {str(e)}"


@tool
async def search_knowledge_base(query: str, db_id: Optional[str] = None) -> str:
    """
    Search the knowledge base using hybrid retrieval (BM25 + Vector Search).
    Use this when the user asks about specific documents or knowledge stored in the system.

    Args:
        query: Search query
        db_id: Optional database ID. If not provided, searches the first available knowledge base.

    Returns:
        Relevant documents
    """
    print(f"step 4.0.1--------------> tool call search_knowledge_base query:{query} db_id:{db_id} ")

    try:
        from src import knowledge_base

        # Get available knowledge bases
        retrievers = knowledge_base.get_retrievers()

        if not retrievers:
            return "No knowledge bases available. Please create a knowledge base first."

        # Determine which knowledge base to query
        target_db_id = db_id
        if not target_db_id:
            # Use the first available knowledge base
            target_db_id = next(iter(retrievers))
            print(f"step 4.0.2--------------> Using first available knowledge base: {target_db_id}")

        if target_db_id not in retrievers:
            available = ", ".join(retrievers.keys())
            return f"Knowledge base '{target_db_id}' not found. Available: {available}"

        # Get the retriever
        retriever_info = retrievers[target_db_id]
        retriever = retriever_info["retriever"]

        # Query the knowledge base
        print(f"step 4.0.3--------------> Querying knowledge base {target_db_id}")
        if inspect.iscoroutinefunction(retriever):
            result = await retriever(query)
        else:
            result = retriever(query)

        # Format the result
        if isinstance(result, list) and result:
            formatted_result = f"Knowledge Base: {retriever_info['name']}\n"
            formatted_result += f"Query: {query}\n\n"
            formatted_result += f"Found {len(result)} relevant documents:\n\n"
            for i, item in enumerate(result[:10], 1):  # Limit to 10 results
                if isinstance(item, dict):
                    content = item.get("content", "")
                    source = item.get("metadata", {}).get("file_name", "Unknown")
                    formatted_result += f"{i}. [{source}]\n{content[:500]}...\n\n"
                else:
                    formatted_result += f"{i}. {str(item)[:500]}...\n\n"
            return formatted_result
        elif isinstance(result, str):
            return result
        else:
            return f"Query completed. Result type: {type(result).__name__}"

    except Exception as e:
        print(f"step 4.0.error--------------> Error searching knowledge base: {e}")
        return f"Error searching knowledge base: {str(e)}"


@tool
def terminal(command: str, timeout: Optional[int] = 30) -> str:
    """
    Execute shell commands in a sandboxed environment.

    Args:
        command: The shell command to execute
        timeout: Optional timeout in seconds (default: 30)

    Returns:
        The output of the command execution

    Example:
        >>> terminal("ls -la")
        'total 16...'
    """
    print(f"step 3.0------------>terminal command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        print(f"step 3.1------------> command result: {result}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"


@tool
def safter_terminal(command: str, timeout: Optional[int] = 30) -> str:
    """
    Execute shell commands in a sandboxed environment.

    Args:
        command: The shell command to execute
        timeout: Optional timeout in seconds (default: 30)
    Returns:
        The output of the command execution

    Example:
        >>> safter_terminal("ls -la")
        'total 16...'
    """
    print(f"step 3.0------------>safter_terminal command: {command}")
    """Execute command with safety checks"""
    # Block dangerous commands
    dangerous_patterns = [
        r'rm\s+-rf\s+/',
        r'sudo\s+',
        r'chmod\s+777',
        r'>\s*/dev/',
        r'curl.*\|.*sh',
        r'wget.*\|.*bash',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return f"Error: Command blocked for security reasons: {command}"

    try:
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            # cwd=str(project_root)
        )

        output = result.stdout
        if result.stderr:
            output += f"\nStderr: {result.stderr}"

        if result.returncode != 0:
            output += f"\nCommand failed with exit code {result.returncode}"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@tool
def python_repl(code: str, timeout: Optional[int] = None) -> str:
    """
    Execute Python code in an isolated REPL environment.

    Use this for calculations, data processing, or running Python scripts.
    The environment persists across calls in the same session.

    Args:
        code: Python code to execute
        timeout: Optional execution timeout in seconds (default: 30)

    Returns:
        Output from execution or error messages

    Examples:
        >>> python_repl("print('Hello')")
        'Hello'

        >>> python_repl("import time\\ntime.sleep(35)", timeout=5)
        'Error: Code execution timed out after 5 seconds'
    """
    print(f"step 1.9.2--------------> tool call python_repl code:{code}  \r\n timeout:{timeout}")
    return _repl_instance.run(code, timeout)


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@tool
def read_file(
              project_root: str,
              file_path: str) -> str:
    """
    Read the content of a file from the local filesystem.

    **CRITICAL for Skills**: Always use this to read SKILL.md before executing any skill.
    Path should be relative to project root (e.g., 'src/agents/mini_openclaw_agent/skills/get_weather/SKILL.md').

    Args:
        project_root:当前项目的根路径
        file_path: Relative path from project root (e.g., 'src/main.py', 'README.md')

    Returns:
        The content of the file or error message

    Examples:
        >>> read_file("README.md")
        '# My Project\\n...'

        >>> read_file("src/agents/mini_openclaw_agent/skills/get_weather/SKILL.md")
        '---\\nname: get_weather\\n...'
    """
    print(f"***------>step 1.0 read_file   file_path:{file_path}   project_root:{project_root} ")
    # 构建完整路径并解析为绝对路径
    full_path = Path(project_root +"/"+ file_path).resolve()
    print(f"------>step 1.1 read_file   full_path:{full_path}")
    # 安全检查：确保路径在项目目录内

    # 检查文件是否存在
    if not full_path.exists():
        print(f"------>step 1.3 File not found at {file_path}")
        return f"Error: File not found at {file_path}"

    # 检查是否为文件
    if not full_path.is_file():
        return f"Error: Path is not a file: {file_path}"

    # 读取文件内容
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content:
            return f"File is empty: {file_path}"
        print(f"------>step 1.4 content len:{len(content)}")
        return content

    except PermissionError:
        return f"Error: Permission denied reading file: {file_path}"
    except UnicodeDecodeError:
        return f"Error: Cannot decode file {file_path} (may be binary file)"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def initialize_core_tools(project_root: Path) -> List:
    """
    初始化所有核心工具

    Args:
        project_root: 项目根目录路径

    Returns:
        工具列表
    """
    tools = []
    print(f"step 0.2  -------------> initialize_core_tools   project_root:{project_root}")
    # 1. Terminal (ShellTool) - 沙箱化命令行
    # shell_tool = ShellTool()
    # tools.append(
    #     Tool(
    #         name="terminal",
    #         func=shell_tool.run,
    #         description=(
    #             "Execute shell commands in a sandboxed environment. "
    #             "Use this to run system commands, manage files, or execute scripts. "
    #             "Note: Dangerous commands like 'rm -rf /' are blocked."
    #         )
    #     )
    # )

    # tools.append(shell_tool)
    # tools.append(terminal)
    tools.append(safter_terminal)

    # 2. Python REPL - Python代码解释器
    # python_repl = PythonREPLTool()
    # tools.append(
    #     Tool(
    #         name="python_repl",
    #         func=python_repl.run,
    #         description=(
    #             "Execute Python code in an isolated REPL environment. "
    #             "Use this for calculations, data processing, or running Python scripts. "
    #             "The environment persists across calls in the same session."
    #         )
    #     )
    # )  python_repl
    tools.append(python_repl)
    # 3. Fetch URL - 网络信息获取（增强版）
    tools.append(fetch_url)

    # 4. Read File - 文件读取工具（限制在项目目录）
    # read_file_tool = ReadFileTool(root_dir=str(project_root))
    # tools.append(
    #     Tool(
    #         name="read_file",
    #         func=read_file_tool.run,
    #         description=(
    #             "Read the content of a file from the local filesystem. "
    #             "**CRITICAL for Skills**: Always use this to read SKILL.md before executing any skill. "
    #             "Path should be relative to project root (e.g., 'skills/get_weather/SKILL.md')."
    #         )
    #     )
    # )
    tools.append(read_file)
    # 5. RAG Search - 知识库检索
    tools.append(search_knowledge_base)

    return tools
