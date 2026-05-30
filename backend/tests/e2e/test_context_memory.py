"""TP0-6: 多轮对话上下文保持 (P0/B4 regression)"""

import pytest
from app.services.memory import session_store
from app.routers.chat import _build_state
from app.models.schemas import ChatRequest


class TestContextMemory:
    @pytest.mark.asyncio
    async def test_build_state_loads_history(self):
        """第二轮对话能加载第一轮的历史"""
        session_store._sessions = {}
        sid = session_store.create_session()
        session_store.add_message(sid, "user", "我叫张三")
        session_store.add_message(sid, "assistant", "你好张三！")
        session_store.set_context(sid, "intent", "general")

        req = ChatRequest(message="我叫什么名字？", conversation_id=sid)
        state = await _build_state(req, sid)

        assert len(state["messages"]) == 2
        assert state["messages"][0]["content"] == "我叫张三"
        assert state["messages"][1]["content"] == "你好张三！"

    @pytest.mark.asyncio
    async def test_interview_context_persists(self):
        """面试上下文跨轮保留"""
        session_store._sessions = {}
        sid = session_store.create_session()
        ctx = {
            "history": [{"role": "assistant", "content": "**第 1 题**"}],
            "questions_asked": 1,
            "evaluations": [],
            "finished": False,
        }
        session_store.set_context(sid, "interview_context", ctx)

        req = ChatRequest(message="我的回答是...", conversation_id=sid)
        state = await _build_state(req, sid)

        assert state["interview_context"] is not None
        assert state["interview_context"]["questions_asked"] == 1

    @pytest.mark.asyncio
    async def test_new_session_has_no_history(self):
        session_store._sessions = {}
        sid = session_store.create_session()
        req = ChatRequest(message="你好", conversation_id=sid)
        state = await _build_state(req, sid)
        assert state["messages"] == []

    @pytest.mark.asyncio
    async def test_resume_text_persists(self):
        """简历文本跨轮保留"""
        session_store._sessions = {}
        sid = session_store.create_session()
        session_store.set_context(sid, "resume_text", "欧阳博亚的简历内容")

        req = ChatRequest(message="继续分析", conversation_id=sid)
        state = await _build_state(req, sid)
        assert state["resume_text"] == "欧阳博亚的简历内容"

    @pytest.mark.asyncio
    async def test_empty_session_returns_defaults(self):
        session_store._sessions = {}
        req = ChatRequest(message="你好")
        state = await _build_state(req, "nonexistent")
        assert state["messages"] == []
        assert state["resume_text"] == ""
