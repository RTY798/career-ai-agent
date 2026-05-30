"""Optimize Agent — 简历优化引擎"""

import logging

from app.agents.llm_client import llm_client
from app.skills.optimize_skill import ResumeOptimizeSkill
from app.models.schemas import AgentState

logger = logging.getLogger(__name__)

optimize_skill = ResumeOptimizeSkill(llm_client)


async def run_optimize_agent(state: AgentState) -> dict:
    """简历优化：检测问题 + 产出对比报告"""
    resume_text = state.get("resume_text", "")
    match_result = state.get("match_result")

    thought = {
        "agent": "简历优化",
        "status": "running",
        "input": f"对简历进行逐段优化分析",
    }
    state["thought_chain"].append(thought)

    if not resume_text:
        state["error"] = "请先上传简历"
        thought["status"] = "error"
        return state

    result = await optimize_skill.execute(resume_text=resume_text, match_result=match_result)
    state["optimize_report"] = result

    n_changes = len(result.get("changes", []))
    thought["status"] = "completed"
    thought["output"] = f"发现 {n_changes} 处可优化点"
    return state
