# """
# Core Tools Implementation for Mini-OpenClaw Agent
# """
# import os
# import re
# import subprocess
# from pathlib import Path
# from typing import Optional, Type
# from bs4 import BeautifulSoup
# import html2text
# from langchain_core.tools import BaseTool
# from langchain_community.tools import ShellTool
# from langchain_experimental.tools import PythonREPLTool
# from langchain_community.tools.file_management import ReadFileTool
# from pydantic import BaseModel, Field
# from backend.config import get_settings
#
# settings = get_settings()
#
#
# class FetchURLTool(BaseTool):
#     """Enhanced URL fetcher with HTML to Markdown conversion"""
#     name: str = "fetch_url"
#     description: str = """
#     Fetches content from a URL and converts it to readable Markdown format.
#     Use this to get web page content for analysis.
#     Input should be a valid URL string.
#     """
#     # safelisted_domains: set = Field(default_factory=set)
#
#     class Inputs(BaseModel):
#         url: str = Field(description="The URL to fetch content from")
#
#     args_schema: Type[BaseModel] = Inputs
#
#     def _run(self, url: str) -> str:
#         """Fetch URL and convert to Markdown"""
#         try:
#             import requests
#             print(f"step 2.0  -------------> FetchURLTool url:{url}")
#             response = requests.get(url, timeout=30, headers={
#                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
#             })
#             response.raise_for_status()
#
#             # Parse HTML and convert to Markdown
#             soup = BeautifulSoup(response.content, 'html.parser')
#             h = html2text.HTML2Text()
#             h.ignore_links = False
#             h.ignore_images = False
#             markdown_content = h.handle(str(soup))
#
#             return markdown_content[:50000]  # Limit to 50k chars
#
#         except Exception as e:
#             return f"Error fetching URL: {str(e)}"
#
#
# class SafeShellTool(ShellTool):
#     """Safe shell tool with sandbox restrictions"""
#     name: str = "terminal"
#     root_dir: str=""
#     description: str = """
#     Execute shell commands in a restricted environment.
#     Commands are limited to the project directory.
#     Dangerous commands (rm -rf, sudo, etc.) are blocked.
#     """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         # Set root directory to project root
#         self.root_dir = str(settings.project_root)
#
#     def _run(self, command: str) -> str:
#         """Execute command with safety checks"""
#         # Block dangerous commands
#         dangerous_patterns = [
#             r'rm\s+-rf\s+/',
#             r'sudo\s+',
#             r'chmod\s+777',
#             r'>\s*/dev/',
#             r'curl.*\|.*sh',
#             r'wget.*\|.*bash',
#         ]
#
#         for pattern in dangerous_patterns:
#             if re.search(pattern, command, re.IGNORECASE):
#                 return f"Error: Command blocked for security reasons: {command}"
#
#         try:
#             # Execute command
#             result = subprocess.run(
#                 command,
#                 shell=True,
#                 capture_output=True,
#                 text=True,
#                 timeout=60,
#                 cwd=str(settings.project_root)
#             )
#
#             output = result.stdout
#             if result.stderr:
#                 output += f"\nStderr: {result.stderr}"
#
#             if result.returncode != 0:
#                 output += f"\nCommand failed with exit code {result.returncode}"
#
#             return output
#
#         except subprocess.TimeoutExpired:
#             return "Error: Command timed out after 60 seconds"
#         except Exception as e:
#             return f"Error executing command: {str(e)}"
#
#
# class CustomPythonREPLTool(PythonREPLTool):
#     """Custom Python REPL tool"""
#     name: str = "python_repl"
#     description: str = """
#     Execute Python code in a REPL environment.
#     Use this for calculations, data processing, and script execution.
#     Input should be valid Python code.
#     """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#
# class SafeReadFileTool(ReadFileTool):
#     """Safe file reading tool restricted to project directory"""
#     name: str = "read_file"
#     description: str = """
#     Read the contents of a file from the project directory.
#     Use this to read skill definitions, configuration files, or other project files.
#     Input should be a file path relative to the project root.
#     """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         # Set root directory to project root
#         if hasattr(self, 'root_dir'):
#             self.root_dir = str(settings.project_root)
#
#     def _run(self, file_path: str) -> str:
#         """Read file with path validation"""
#         try:
#             # Resolve path relative to project root
#             print(f"step 1.6  -------------> SafeReadFileTool file_path:{file_path}")
#             full_path = (settings.project_root / file_path).resolve()
#             print(f"step 1.7  -------------> SafeReadFileTool full_path:{full_path}")
#             # Security check: ensure path is within project root
#             if not str(full_path).startswith(str(settings.project_root)):
#                 return f"Error: Access denied - path outside project root: {file_path}"
#
#             if not full_path.exists():
#                 return f"Error: File not found: {file_path}"
#
#             if not full_path.is_file():
#                 return f"Error: Path is not a file: {file_path}"
#
#             # Read file content
#             with open(full_path, 'r', encoding='utf-8') as f:
#                 content = f.read()
#
#             # Limit size
#             if len(content) > 100000:
#                 content = content[:100000] + "\n\n...[truncated, file too large]"
#             print(f"step 1.8  -------------> SafeReadFileTool content length:{len(content)}")
#             return content
#
#         except Exception as e:
#             return f"Error reading file: {str(e)}"
#
#
# class RAGRetrievalTool(BaseTool):
#     """RAG-based knowledge retrieval tool using LlamaIndex"""
#     name: str = "search_knowledge_base"
#     description: str = """
#     Search the knowledge base for relevant information.
#     Use this when the user asks about specific knowledge or documentation.
#     Input should be a search query string.
#     """
#     index_dir: Path = Field(default_factory=lambda: settings.storage_dir)
#
#     class Inputs(BaseModel):
#         query: str = Field(description="Search query for the knowledge base")
#
#     args_schema: Type[BaseModel] = Inputs
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self._index = None
#         self._query_engine = None
#
#     def _build_index(self):
#         """Build or load the RAG index"""
#         try:
#             from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
#             from llama_index.core.node_parser import SentenceSplitter
#             from langchain_openai import OpenAIEmbeddings
#             from langchain_community.vectorstores import FAISS
#             from langchain_text_splitters import RecursiveCharacterTextSplitter
#             # from llama_index.embeddings.openai import OpenAIEmbedding
#             from llama_index.embeddings.huggingface import HuggingFaceEmbedding
#             embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")
#
#             # Initialize embedding model
#             # embedding_model = OpenAIEmbeddings()
#             # embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)
#
#             # Check if index exists
#             index_path = self.index_dir / "index"
#             if index_path.exists():
#                 # Load existing index
#                 from llama_index.core import StorageContext, load_index_from_storage
#                 storage_context = StorageContext.from_defaults(str(index_path))
#                 self._index = load_index_from_storage(storage_context)
#             else:
#                 # Build new index
#                 if not settings.knowledge_dir.exists():
#                     return False
#
#                 documents = SimpleDirectoryReader(
#                     str(settings.knowledge_dir)
#                 ).load_data()
#
#                 splitter = SentenceSplitter(
#                     chunk_size=settings.chunk_size,
#                     chunk_overlap=settings.chunk_overlap
#                 )
#
#                 self._index = VectorStoreIndex.from_documents(
#                     documents,
#                     transform=splitter,
#                     embed_model=embed_model
#                 )
#
#                 # Persist index
#                 self._index.storage_context.persist(str(index_path))
#
#             # Create query engine
#             self._query_engine = self._index.as_query_engine(
#                 similarity_top_k=settings.top_k,
#                 streaming=False
#             )
#
#             return True
#
#         except Exception as e:
#             print(f"Error building RAG index: {e}")
#             return False
#
#     def _run(self, query: str) -> str:
#         """Search knowledge base"""
#         try:
#             # Lazy initialization
#             if self._query_engine is None:
#                 success = self._build_index()
#                 if not success:
#                     return "Error: Knowledge base not available or empty"
#
#             # Perform search
#             response = self._query_engine.query(query)
#
#             # Format results
#             results = f"Search Query: {query}\n\n"
#             results += f"Answer: {str(response)}\n\n"
#
#             # Add source information
#             if hasattr(response, 'source_nodes'):
#                 results += "Sources:\n"
#                 for i, node in enumerate(response.source_nodes, 1):
#                     source_info = node.metadata.get('file_name', 'Unknown')
#                     results += f"{i}. {source_info}\n"
#
#             return results
#
#         except Exception as e:
#             return f"Error searching knowledge base: {str(e)}"
#
#
# def get_core_tools():
#     """Get all core tools"""
#     return [
#         SafeShellTool(),
#         CustomPythonREPLTool(),
#         FetchURLTool(),
#         SafeReadFileTool(),
#         RAGRetrievalTool(),
#     ]
