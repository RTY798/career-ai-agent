"""TP1-1: Summary Agent 各意图格式化输出 (P1)"""

import pytest
from app.agents.summary_agent import run_summary_agent


class TestSummaryAgent:
    @pytest.mark.asyncio
    async def test_resume_analyze_contains_score(self, mock_agent_state):
        state = mock_agent_state.copy()
        state["intent"] = "resume_analyze"
        state["parsed_resume"] = {
            "match_score": 75,
            "summary": "匹配度良好",
            "skills_match": [{"name": "Python", "status": "matched", "importance": "required"}],
            "skills_gap": [{"name": "Docker", "status": "missing", "importance": "preferred"}],
            "suggestions": [{"category": "content", "text": "补充Docker", "priority": "high"}],
            "interview_questions": [{"question": "用Python做过什么？", "category": "technical"}],
        }
        result = await run_summary_agent(state)
        resp = result.get("final_response", "")
        assert "75" in resp
        assert "Python" in resp
        assert "Docker" in resp
        assert "简历分析" in resp or "匹配" in resp

    @pytest.mark.asyncio
    async def test_match_position_contains_comparison(self, mock_agent_state):
        state = mock_agent_state.copy()
        state["intent"] = "match_position"
        state["match_result"] = {
            "match_score": 80,
            "summary": "匹配",
            "skills_match": [{"name": "Python", "status": "matched", "importance": "required"}],
            "skills_gap": [{"name": "K8s", "status": "missing", "importance": "preferred"}],
            "suggestions": [{"category": "keyword", "text": "学K8s", "priority": "high"}],
        }
        result = await run_summary_agent(state)
        resp = result.get("final_response", "")
        assert "80" in resp
        assert "Python" in resp
        assert "K8s" in resp

    @pytest.mark.asyncio
    async def test_optimize_resume_shows_changes(self, mock_agent_state):
        state = mock_agent_state.copy()
        state["intent"] = "optimize_resume"
        state["optimize_report"] = {
            "changes": [
                {"section_index": 0, "original_text": "负责开发", "optimized_text": "设计并实现",
                 "issue_type": "weak_verb", "reason": "空洞动词", "expected_impact": "high"},
            ],
            "optimized_resume": "设计并实现了系统",
            "total_improvement": 5,
        }
        result = await run_summary_agent(state)
        resp = result.get("final_response", "")
        assert "空洞动词" in resp or "修改" in resp
        assert "负责开发" in resp
        assert "设计并实现" in resp

    @pytest.mark.asyncio
    async def test_career_advice_uses_retrieved_docs(self, mock_llm, mock_agent_state):
        state = mock_agent_state.copy()
        state["intent"] = "career_advice"
        state["user_message"] = "AI Agent需要学什么？"
        state["retrieved_docs"] = [
            {"content": "LangGraph是Agent开发的核心框架", "metadata": {"source": "career-guide"}},
        ]
        state["messages"] = []
        result = await run_summary_agent(state)
        resp = result.get("final_response", "")
        assert resp is not None

    @pytest.mark.asyncio
    async def test_general_returns_polite_reply(self, mock_llm, mock_agent_state):
        state = mock_agent_state.copy()
        state["intent"] = "general"
        state["user_message"] = "你好"
        result = await run_summary_agent(state)
        resp = result.get("final_response", "")
        assert resp is not None
        assert len(resp) > 0

    @pytest.mark.asyncio
    async def test_interview_finished_contains_report(self, mock_agent_state):
        state = mock_agent_state.copy()
        state["intent"] = "general"
        state["interview_context"] = {
            "finished": True,
            "report": {
                "overall_score": 72,
                "dimension_scores": {"technical": 70, "project": 75, "behavioral": 70, "communication": 73},
                "strengths": ["技术基础扎实"],
                "weaknesses": ["经验不足"],
                "improvement_plan": ["多刷题"],
                "question_reviews": [],
            },
        }
        result = await run_summary_agent(state)
        resp = result.get("final_response", "")
        assert "72" in resp

    @pytest.mark.asyncio
    async def test_no_data_does_not_crash(self, mock_llm, mock_agent_state):
        state = mock_agent_state.copy()
        state["intent"] = "resume_analyze"
        state["parsed_resume"] = None
        result = await run_summary_agent(state)
        assert result.get("final_response") is not None
