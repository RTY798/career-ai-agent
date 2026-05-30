"""Match Agent — 人岗匹配分析"""

import logging

from app.agents.llm_client import llm_client
from app.skills.match_skill import MatchAnalysisSkill
from app.models.schemas import AgentState

logger = logging.getLogger(__name__)

match_skill = MatchAnalysisSkill(llm_client)


async def run_match_agent(state: AgentState) -> dict:
    """简历 vs JD 匹配分析"""
    resume_text = state.get("resume_text", "")
    jd_text = state.get("jd_text", "")

    thought = {
        "agent": "岗位匹配",
        "status": "running",
        "input": f"简历 vs 岗位描述匹配分析",
    }
    state["thought_chain"].append(thought)

    if not resume_text or not jd_text:
        state["error"] = "请同时提供简历和职位描述"
        thought["status"] = "error"
        return state

    result = await match_skill.execute(resume_text=resume_text, jd_text=jd_text)
    state["match_result"] = result

    thought["status"] = "completed"
    thought["output"] = f"匹配度: {result.get('match_score', 0)}分"
    return state
