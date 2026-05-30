"""TP0-5: SSE 事件序列 + 内容语义验证 (P0/smoke)"""

import json
import pytest
from app.routers.chat import _sse_event, _build_state
from app.models.schemas import ChatRequest
from app.services.memory import session_store


def test_sse_event_format():
    """验证 SSE 事件格式正确"""
    event = _sse_event("thought", {"agent": "test", "status": "completed"})
    assert event.startswith("event: thought\n")
    assert "\ndata: " in event
    assert event.endswith("\n\n")
    data = json.loads(event.split("\ndata: ")[1].strip())
    assert data["agent"] == "test"


def test_sse_event_with_unicode():
    event = _sse_event("message", {"content": "你好世界"})
    assert "你好世界" in event


@pytest.mark.asyncio
async def test_stream_events_sequence(mock_llm, mock_agent_state):
    """验证 _stream_events 产出的事件序列"""
    from app.routers.chat import _stream_events
    from unittest.mock import patch

    # Patch llm_client in router_agent
    import app.agents.router_agent as ra
    original = ra.llm_client
    ra.llm_client = mock_llm

    try:
        events = []
        async for event in _stream_events(
            ChatRequest(message="hello"),
            mock_agent_state,
        ):
            events.append(event)

        event_types = []
        for e in events:
            for line in e.split("\n"):
                if line.startswith("event: "):
                    event_types.append(line[7:].strip())

        # 关键路径事件序列
        assert "thought" in event_types
        assert "message" in event_types
        assert "done" in event_types

        # message 事件必须有内容
        for e in events:
            for line in e.split("\n"):
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if "content" in data:
                            assert data["content"].strip() != ""
                            assert "好的，让我处理你的请求" not in data["content"]
                    except json.JSONDecodeError:
                        pass

    finally:
        ra.llm_client = original


@pytest.mark.asyncio
async def test_stream_with_resume_intent(mock_llm):
    """简历分析意图的 SSE 流"""
    from app.routers.chat import _stream_events
    from app.models.schemas import ChatRequest
    import app.agents.router_agent as ra

    original = ra.llm_client

    class ResumeLLM:
        async def complete(self, **kw):
            if "路由助手" in kw.get("system_prompt", ""):
                return {"content": '{"intent": "resume_analyze", "reason": "test"}', "usage": {}}
            return await mock_llm.complete(**kw)

    ra.llm_client = ResumeLLM()

    try:
        state = {
            "user_message": "分析简历",
            "messages": [],
            "intent": None,
            "resume_text": "test resume content",
            "jd_text": "test jd",
            "parsed_resume": None,
            "match_result": None,
            "optimize_report": None,
            "retrieved_docs": [],
            "interview_context": None,
            "final_response": None,
            "thought_chain": [],
            "error": None,
        }
        events = []
        async for event in _stream_events(ChatRequest(message="分析简历"), state):
            events.append(event)

        assert len(events) >= 4  # thought, thought, message, done

    finally:
        ra.llm_client = original
