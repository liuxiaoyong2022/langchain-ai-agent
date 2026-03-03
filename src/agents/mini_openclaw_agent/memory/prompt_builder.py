"""
System Prompt 动态构建器
按照 PRD 规定的6个部分顺序拼接
"""
from pathlib import Path
from typing import Dict, List


class PromptBuilder:
    """
    负责从文件系统读取并拼接 System Prompt
    """

    def __init__(self, workspace_dir: Path, memory_dir: Path, skills_dir: Path):
        self.workspace_dir = workspace_dir
        self.memory_dir = memory_dir
        self.skills_dir = skills_dir

        # Token限制（单文件最大字符数）
        self.MAX_FILE_CHARS = 20000

    def _read_file_safe(self, file_path: Path) -> str:
        """
        安全读取文件，超长自动截断

        Args:
            file_path: 文件路径

        Returns:
            文件内容
        """
        if not file_path.exists():
            return ""

        try:
            content = file_path.read_text(encoding='utf-8')

            if len(content) > self.MAX_FILE_CHARS:
                content = content[:self.MAX_FILE_CHARS] + "\n\n...[truncated due to length]"

            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def build_skills_snapshot(self) -> str:
        """
        扫描 skills 目录，生成 SKILLS_SNAPSHOT.md

        Returns:
            XML格式的技能列表
        """
        snapshot_lines = ["<available_skills>"]

        # 遍历所有技能文件夹
        if not self.skills_dir.exists():
            snapshot_lines.append("  <!-- No skills found -->")
        else:
            for skill_dir in self.skills_dir.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                # 读取元数据（简化版解析）
                try:
                    lines = skill_md.read_text(encoding='utf-8').split('\n')
                    name = skill_dir.name
                    description = "No description"

                    # 尝试提取标题和描述
                    for line in lines[:20]:
                        if line.startswith("# "):
                            name = line.replace("# ", "").strip()
                        if "描述" in line or "description" in line.lower():
                            if ":" in line:
                                description = line.split(":", 1)[1].strip()

                    # 相对路径
                    location = f"./skills/{skill_dir.name}/SKILL.md"

                    snapshot_lines.append("  <skill>")
                    snapshot_lines.append(f"    <name>{name}</name>")
                    snapshot_lines.append(f"    <description>{description}</description>")
                    snapshot_lines.append(f"    <location>{location}</location>")
                    snapshot_lines.append("  </skill>")
                except Exception as e:
                    continue

        snapshot_lines.append("</available_skills>")

        return "\n".join(snapshot_lines)

    def build_system_prompt(self) -> str:
        """
        按照 PRD 规定的顺序拼接 System Prompt

        顺序：
        1. SKILLS_SNAPSHOT.md (能力列表)
        2. SOUL.md (核心设定)
        3. IDENTITY.md (自我认知)
        4. USER.md (用户画像)
        5. AGENTS.md (行为准则 & 记忆操作指南)
        6. MEMORY.md (长期记忆)

        Returns:
            完整的系统提示词
        """
        parts = []

        # 1. SKILLS_SNAPSHOT
        skills_snapshot = self.build_skills_snapshot()
        print(f" step 0.8.1   PromptBuilder---------->   skills_snapshot:{skills_snapshot}")
        if skills_snapshot:
            parts.append(f"# Available Skills\n\n{skills_snapshot}")

        # 2. SOUL.md (核心设定)
        soul = self._read_file_safe(self.workspace_dir / "SOUL.md")
        if soul:
            parts.append(f"# Core Identity\n\n{soul}")

        # 3. IDENTITY.md (自我认知)
        identity = self._read_file_safe(self.workspace_dir / "IDENTITY.md")
        if identity:
            parts.append(f"# Self Awareness\n\n{identity}")

        # 4. USER.md (用户画像)
        user_profile = self._read_file_safe(self.workspace_dir / "USER.md")
        if user_profile:
            parts.append(f"# User Profile\n\n{user_profile}")

        # 5. AGENTS.md (行为准则 & 技能协议)
        agents = self._read_file_safe(self.workspace_dir / "AGENTS.md")
        if agents:
            parts.append(f"# Operational Guidelines\n\n{agents}")

        # 6. MEMORY.md (长期记忆)
        memory = self._read_file_safe(self.memory_dir / "MEMORY.md")
        if memory:
            parts.append(f"# Long-term Memory\n\n{memory}")

        return "\n\n---\n\n".join(parts)