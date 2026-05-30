"""TP0-2: SessionStore 完整 CRUD + 并发写入竞态 (P0)"""

import asyncio
import pytest
from app.services.memory import SessionStore


class TestSessionStore:
    @pytest.fixture
    def store(self):
        s = SessionStore()
        s._sessions = {}  # clear singleton state
        s._expire_after = 3600
        yield s

    def test_create_session(self, store):
        sid = store.create_session()
        assert sid is not None
        assert len(sid) > 0

    def test_get_session_exists(self, store):
        sid = store.create_session()
        session = store.get_session(sid)
        assert session is not None
        assert "messages" in session
        assert "context" in session

    def test_get_session_not_found(self, store):
        result = store.get_session("nonexistent")
        assert result is None

    def test_set_and_get_context(self, store):
        sid = store.create_session()
        store.set_context(sid, "intent", "general")
        assert store.get_context(sid, "intent") == "general"

    def test_get_context_default(self, store):
        sid = store.create_session()
        assert store.get_context(sid, "missing", "default_val") == "default_val"

    def test_get_context_from_nonexistent(self, store):
        assert store.get_context("invalid", "key") is None

    def test_add_and_get_messages(self, store):
        sid = store.create_session()
        store.add_message(sid, "user", "你好")
        store.add_message(sid, "assistant", "你好！")
        history = store.get_history(sid)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "你好"
        assert history[1]["role"] == "assistant"

    def test_get_history_limit(self, store):
        sid = store.create_session()
        for i in range(10):
            store.add_message(sid, "user", f"msg{i}")
        history = store.get_history(sid, limit=5)
        assert len(history) == 5
        assert history[0]["content"] == "msg5"
        assert history[-1]["content"] == "msg9"

    def test_get_history_from_nonexistent(self, store):
        assert store.get_history("invalid") == []

    def test_session_expiry(self, store):
        import time
        sid = store.create_session()
        store._expire_after = 0  # expire immediately
        store._sessions[sid]["last_active"] = 0
        result = store.get_session(sid)
        assert result is None

    def test_add_message_creates_session_implicitly(self, store):
        store.add_message("new_sid", "user", "auto create")
        hist = store.get_history("new_sid")
        assert len(hist) == 1

    def test_set_context_updates_last_active(self, store):
        sid = store.create_session()
        old_time = store._sessions[sid]["last_active"]
        import time
        time.sleep(0.01)
        store.set_context(sid, "key", "val")
        assert store._sessions[sid]["last_active"] > old_time

    @pytest.mark.asyncio
    async def test_concurrent_writes(self, store):
        """验证并发写入不丢数据"""
        sid = store.create_session()

        async def write_msg(i):
            store.add_message(sid, "user", f"concurrent_msg_{i}")

        await asyncio.gather(*[write_msg(i) for i in range(10)])
        history = store.get_history(sid, limit=20)
        msgs = [m["content"] for m in history if m["content"].startswith("concurrent_msg_")]
        assert len(msgs) == 10
        for i in range(10):
            assert f"concurrent_msg_{i}" in msgs
