"""标准化 Skill 基类 — 所有 Agent Skills 继承此基类"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.agents.llm_client import LLMClientManager


class BaseSkill(ABC):
    """所有 Skill 的基类，封装 Prompt + 解析 + 版本号"""

    name: str = "base"
    version: str = "0.1.0"

    def __init__(self, llm_client: LLMClientManager):
        self.llm_client = llm_client

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """执行 Skill，返回结构化结果"""

    def _parse_json(self, text: str) -> Optional[dict]:
        """从 LLM 响应中解析 JSON，支持 markdown code block 回退"""
        import json
        import re

        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown code block 中提取
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        return None
