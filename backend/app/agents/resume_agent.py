"""Resume Agent — 简历解析 + 分层 Prompt 分析"""

import logging

from app.agents.llm_client import llm_client
from app.skills.resume_skill import ResumeAnalysisSkill
from app.models.schemas import AgentState

logger = logging.getLogger(__name__)

resume_skill = ResumeAnalysisSkill(llm_client)


async def run_resume_agent(state: AgentState) -> dict:
    """解析并分析简历"""
    resume_text = state.get("resume_text", "")
    jd_text = state.get("jd_text", "")

    thought = {
        "agent": "简历分析",
        "status": "running",
        "input": f"简历长度: {len(resume_text)}字, JD: {len(jd_text)}字",
    }
    state["thought_chain"].append(thought)

    if not resume_text:
        state["error"] = "请先上传简历"
        thought["status"] = "error"
        return state

    result = await resume_skill.execute(resume_text=resume_text, jd_text=jd_text)
    state["parsed_resume"] = result

    thought["status"] = "completed"
    thought["output"] = f"匹配度: {result.get('match_score', 0)}分, 技能匹配: {len(result.get('skills_match', []))}项"
    return state
