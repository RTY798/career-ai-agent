"""LangGraph 主图 — 6 Agent 协同工作流"""

import logging

from langgraph.graph import StateGraph, END

from app.models.schemas import AgentState
from app.agents.router_agent import classify_intent, route_decision
from app.agents.resume_agent import run_resume_agent
from app.agents.match_agent import run_match_agent
from app.agents.optimize_agent import run_optimize_agent
from app.agents.interview_agent import run_interview_agent
from app.agents.knowledge_agent import run_knowledge_agent
from app.agents.summary_agent import run_summary_agent

logger = logging.getLogger(__name__)


def create_graph():
    """构建 LangGraph StateGraph"""
    workflow = StateGraph(AgentState)

    workflow.add_node("router", run_router)
    workflow.add_node("resume_agent", run_resume_agent)
    workflow.add_node("match_agent", run_match_agent)
    workflow.add_node("optimize_agent", run_optimize_agent)
    workflow.add_node("interview_agent", run_interview_agent)
    workflow.add_node("knowledge_agent", run_knowledge_agent)
    workflow.add_node("summary_agent", run_summary_agent)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        lambda state: route_decision(state.get("intent", "general")),
        {
            "resume_agent": "resume_agent",
            "match_agent": "match_agent",
            "optimize_agent": "optimize_agent",
            "interview_agent": "interview_agent",
            "knowledge_agent": "knowledge_agent",
            "summary_agent": "summary_agent",
        },
    )

    workflow.add_edge("resume_agent", "summary_agent")
    workflow.add_edge("match_agent", "summary_agent")
    workflow.add_edge("optimize_agent", "summary_agent")
    workflow.add_edge("interview_agent", END)
    workflow.add_edge("knowledge_agent", "summary_agent")
    workflow.add_edge("summary_agent", END)

    return workflow.compile()


async def run_router(state: AgentState) -> dict:
    """Router 节点：意图分类，考虑面试上下文"""
    user_message = state.get("user_message", "")
    interview_ctx = state.get("interview_context")

    result = await classify_intent(user_message, interview_ctx)
    state["intent"] = result["intent"]

    thought = {
        "agent": "意图识别",
        "status": "completed",
        "input": user_message[:100],
        "output": result["label"],
    }
    state["thought_chain"].append(thought)

    if result.get("end_interview"):
        state["interview_context"] = {"finished": True, **state.get("interview_context", {})}

    logger.info("routed", extra={"intent": result["intent"], "label": result["label"]})
    return state


agent_graph = create_graph()
