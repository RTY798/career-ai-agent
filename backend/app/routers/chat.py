"""SSE 流式聊天端点 — 真流式逐节点推送"""

import json
import asyncio
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.graph import agent_graph
from app.models.schemas import AgentState, ChatRequest
from app.services.memory import session_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """同步聊天（非流式）"""
    conv_id = request.conversation_id or session_store.create_session()
    state = await _build_state(request, conv_id)

    try:
        result = await agent_graph.ainvoke(state)
    except Exception as e:
        logger.error(f"graph_invoke_failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    _save_session(conv_id, request, result)

    return {
        "reply": result.get("final_response", ""),
        "intent": result.get("intent"),
        "thought_chain": result.get("thought_chain", []),
        "parsed_resume": result.get("parsed_resume"),
        "match_result": result.get("match_result"),
        "optimize_report": result.get("optimize_report"),
        "interview_report": (
            result.get("parsed_resume", {}).get("interview_report")
            if result.get("parsed_resume")
            else None
        ),
        "conversation_id": conv_id,
    }


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE 流式聊天 — 逐节点推送 Agent 思考过程"""
    conv_id = request.conversation_id or session_store.create_session()
    initial_state = await _build_state(request, conv_id)

    async def _stream_and_save():
        """流式推送，结束后保存会话状态"""
        final_state = None
        async for event in _stream_events(request, initial_state):
            if event.startswith("event: message"):
                # 提取 final_state 用于保存 session
                pass
            yield event

        # 流结束后保存 interview_context
        if final_state and final_state.get("interview_context"):
            session_store.set_context(conv_id, "interview_context", final_state["interview_context"])

    return StreamingResponse(
        _stream_and_save(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_events(request: ChatRequest, initial_state: AgentState) -> AsyncGenerator[str, None]:
    """独立 generator 函数，逐节点推送 SSE 事件"""
    state = initial_state
    try:
        from app.agents.router_agent import classify_intent, route_decision

        # 1. Router — 带面试上下文
        interview_ctx = state.get("interview_context")
        router_result = await classify_intent(request.message, interview_ctx)
        intent = router_result["intent"]
        state["intent"] = intent
        if router_result.get("end_interview"):
            if interview_ctx is None:
                interview_ctx = {}
            interview_ctx["finished"] = True
            state["interview_context"] = interview_ctx
        thought = {"agent": "意图识别", "status": "completed", "output": router_result["label"]}
        state["thought_chain"].append(thought)
        yield _sse_event("thought", thought)

        # 2. 路由到对应 Agent
        next_node = route_decision(intent)
        agent_map = {
            "resume_agent": ("resume_agent", _run_resume_agent),
            "match_agent": ("match_agent", _run_match_agent),
            "optimize_agent": ("optimize_agent", _run_optimize_agent),
            "interview_agent": ("interview_agent", _run_interview_agent),
            "knowledge_agent": ("knowledge_agent", _run_knowledge_agent),
        }

        agent_entry = agent_map.get(next_node)
        if agent_entry:
            name, fn = agent_entry
            yield _sse_event("thought", {"agent": name, "status": "running"})
            try:
                state = await fn(state)
                if state.get("thought_chain"):
                    yield _sse_event("thought", state["thought_chain"][-1])
            except Exception as e:
                yield _sse_event("thought", {"agent": name, "status": "error", "error": str(e)})
            await asyncio.sleep(0.05)

        # 3. Summary（interview 自带回复）
        if next_node != "interview_agent":
            yield _sse_event("thought", {"agent": "整合回复", "status": "running"})
            try:
                state = await _run_summary_agent(state)
                if state.get("thought_chain"):
                    yield _sse_event("thought", state["thought_chain"][-1])
            except Exception as e:
                yield _sse_event("thought", {"agent": "整合回复", "status": "error", "error": str(e)})

        # 4. 最终消息
        response_text = state.get("final_response", "")
        yield _sse_event("message", {"content": response_text})

        # 5. 面试报告
        pr = state.get("parsed_resume")
        if pr and isinstance(pr, dict) and pr.get("interview_report"):
            yield _sse_event("report", pr["interview_report"])

    except Exception as e:
        logger.error(f"stream_failed: {e}")
        yield _sse_event("error", {"error": str(e)})
    finally:
        yield _sse_event("done", {})


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _save_session(conv_id: str, request: ChatRequest, result: dict):
    """保存会话状态"""
    session_store.add_message(conv_id, "user", request.message)
    session_store.add_message(conv_id, "assistant", result.get("final_response", ""))
    session_store.set_context(conv_id, "intent", result.get("intent"))
    if result.get("interview_context"):
        session_store.set_context(conv_id, "interview_context", result["interview_context"])


async def _build_state(request: ChatRequest, conv_id: str) -> AgentState:
    """构建初始 AgentState（含面试上下文恢复）"""
    state: AgentState = {
        "user_message": request.message,
        "messages": session_store.get_history(conv_id, limit=10),
        "intent": None,
        "resume_text": request.resume or session_store.get_context(conv_id, "resume_text", ""),
        "jd_text": request.jd or session_store.get_context(conv_id, "jd_text", ""),
        "parsed_resume": None,
        "match_result": None,
        "optimize_report": None,
        "retrieved_docs": [],
        "interview_context": session_store.get_context(conv_id, "interview_context"),
        "final_response": None,
        "thought_chain": [],
        "error": None,
    }
    return state


# ── 本地 Agent 运行封装 ──

async def _run_resume_agent(state: AgentState) -> AgentState:
    from app.agents.resume_agent import run_resume_agent
    return await run_resume_agent(state)

async def _run_match_agent(state: AgentState) -> AgentState:
    from app.agents.match_agent import run_match_agent
    return await run_match_agent(state)

async def _run_optimize_agent(state: AgentState) -> AgentState:
    from app.agents.optimize_agent import run_optimize_agent
    return await run_optimize_agent(state)

async def _run_interview_agent(state: AgentState) -> AgentState:
    from app.agents.interview_agent import run_interview_agent
    return await run_interview_agent(state)

async def _run_knowledge_agent(state: AgentState) -> AgentState:
    from app.agents.knowledge_agent import run_knowledge_agent
    return await run_knowledge_agent(state)

async def _run_summary_agent(state: AgentState) -> AgentState:
    from app.agents.summary_agent import run_summary_agent
    return await run_summary_agent(state)
