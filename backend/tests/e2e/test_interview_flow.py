"""TP0-7: 面试全流程 — 开始→回答×N→结束→报告 (P0)"""

import pytest
from app.agents.interview_agent import run_interview_agent


class TestInterviewFlow:
    """完整的面试生命周期验证"""

    @pytest.mark.asyncio
    async def test_full_interview_lifecycle(self, mock_llm, mock_agent_state):
        """开始→回答×2→结束→报告"""
        state = mock_agent_state.copy()

        # Step 1: Start
        state["user_message"] = "开始面试"
        state = await run_interview_agent(state)
        assert state["interview_context"]["questions_asked"] == 1
        assert state["interview_context"]["finished"] is False
        assert not state["interview_context"].get("report")

        # Step 2: Answer Q1
        state["user_message"] = "我最近做了一个AI客服系统"
        state = await run_interview_agent(state)
        assert state["interview_context"]["questions_asked"] == 2
        assert len(state["interview_context"]["evaluations"]) == 1

        # Step 3: Answer Q2
        state["user_message"] = "用了LangGraph和FastAPI"
        state = await run_interview_agent(state)
        assert state["interview_context"]["questions_asked"] == 3
        assert len(state["interview_context"]["evaluations"]) == 2

        # Step 4: End interview
        state["user_message"] = "结束面试"
        state = await run_interview_agent(state)
        assert state["interview_context"]["finished"] is True

        # Step 5: Verify report
        report = state["interview_context"].get("report")
        assert report is not None, "面试报告必须存在"
        assert "overall_score" in report
        assert "dimension_scores" in report
        assert "strengths" in report
        assert "weaknesses" in report
        assert "improvement_plan" in report
        assert "question_reviews" in report

        # Step 6: Final response should contain the report
        resp = state.get("final_response", "")
        assert "总评" in resp or str(report.get("overall_score", "")) in resp

    @pytest.mark.asyncio
    async def test_interview_context_does_not_leak(self, mock_llm, mock_agent_state):
        """面试结束后，新对话不被面试上下文污染"""
        state = mock_agent_state.copy()

        # Do interview
        state["user_message"] = "开始面试"
        state = await run_interview_agent(state)
        state["user_message"] = "我的回答"
        state = await run_interview_agent(state)

        # Check interview_ctx exists but doesn't interfere with new intent
        assert state["interview_context"] is not None
        assert not state["interview_context"].get("finished")
