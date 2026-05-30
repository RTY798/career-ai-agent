"""对话记忆管理 — session store，多轮上下文"""

import time
import uuid
from typing import Optional


class SessionStore:
    """简单的内存 Session 存储（生产环境应替换为 Redis）"""

    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._expire_after = 3600  # 1小时后过期

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "messages": [],
            "created_at": time.time(),
            "last_active": time.time(),
            "context": {},
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        # 检查是否过期
        if time.time() - session["last_active"] > self._expire_after:
            del self._sessions[session_id]
            return None
        return session

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[dict] = None):
        session = self.get_session(session_id)
        if not session:
            session = {"messages": [], "context": {}}
            self._sessions[session_id] = session
        session["messages"].append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": time.time(),
        })
        session["last_active"] = time.time()

    def get_context(self, session_id: str, key: str, default=None):
        session = self.get_session(session_id)
        if not session:
            return default
        return session["context"].get(key, default)

    def set_context(self, session_id: str, key: str, value):
        session = self.get_session(session_id)
        if not session:
            return
        session["context"][key] = value
        session["last_active"] = time.time()

    def get_history(self, session_id: str, limit: int = 10) -> list[dict]:
        session = self.get_session(session_id)
        if not session:
            return []
        return session["messages"][-limit:]


session_store = SessionStore()
