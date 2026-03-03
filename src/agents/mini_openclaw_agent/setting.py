"""
Configuration management for Mini-OpenClaw
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # # DeepSeek API
    # deepseek_api_key: str
    # deepseek_base_url: str = "https://api.deepseek.com/v1"
    # deepseek_model:str
    # # Server
    # host: str = "0.0.0.0"
    # port: int = 8002

    # # Paths
    # project_root: Path
    # skills_dir: Path
    # memory_dir: Path
    # sessions_dir: Path
    # workspace_dir: Path
    knowledge_dir: Path=Path("src/agents/mini_openclaw_agent/miniknowledge")
    storage_dir: Path=Path("src/agents/mini_openclaw_agent/storage")

    # RAG Configuration
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5



    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert paths to Path objects
        # self.project_root = Path(self.project_root)
        # self.skills_dir = Path(self.skills_dir)
        # self.memory_dir = Path(self.memory_dir)
        # self.sessions_dir = Path(self.sessions_dir)
        # self.workspace_dir = Path(self.workspace_dir)
        self.knowledge_dir = Path(self.knowledge_dir)
        self.storage_dir = Path(self.storage_dir)

        # Create directories if they don't exist
        # for dir_path in [self.skills_dir, self.memory_dir, self.sessions_dir,
        #                  self.workspace_dir, self.knowledge_dir, self.storage_dir]:
        #     dir_path.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
