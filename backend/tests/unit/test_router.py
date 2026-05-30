"""TP0-3: Router 面试短路 + 干扰过滤 (P0/smoke)"""

import pytest
from app.agents.router_agent import classify_intent, route_decision


class TestClassifyIntent:
    @pytest.mark.asyncio
    async def test_interview_ongoing_returns_mock_interview(self, mock_llm):
        """面试中，普通消息 → 保持面试"""
        ctx = {"finished": False, "questions_asked": 3}
        result = await classify_intent("我觉得这个项目用了Redis", ctx)
        assert result["intent"] == "mock_interview"
        assert "end_interview" not in result or not result["end_interview"]

    @pytest.mark.asyncio
    async def test_interview_ongoing_end_request(self, mock_llm):
        """面试中，说结束 → 标记结束"""
        ctx = {"finished": False, "questions_asked": 2}
        result = await classify_intent("结束面试", ctx)
        assert result["intent"] == "mock_interview"
        assert result.get("end_interview") is True

    @pytest.mark.asyncio
    async def test_interview_blocks_distraction(self, mock_llm):
        """面试中，查薪资等干扰 → 仍然保持面试"""
        ctx = {"finished": False, "questions_asked": 1}
        result = await classify_intent("帮我查一下薪资待遇", ctx)
        assert result["intent"] == "mock_interview"

    @pytest.mark.asyncio
    async def test_no_interview_context_uses_llm(self, mock_llm):
        """无面试上下文 → LLM 正常分类"""
        result = await classify_intent("你好", None)
        assert result["intent"] == "general"

    @pytest.mark.asyncio
    async def test_interview_finished_uses_llm(self, mock_llm):
        """面试已结束 → LLM 正常分类"""
        ctx = {"finished": True}
        result = await classify_intent("你好", ctx)
        assert result["intent"] == "general"

    @pytest.mark.asyncio
    async def test_interview_empty_context_is_same_as_none(self, mock_llm):
        ctx = {}
        result = await classify_intent("你好", ctx)
        assert result["intent"] == "general"

    @pytest.mark.asyncio
    async def test_interview_end_with_substring(self, mock_llm):
        """B3 regression: 子串也能触发结束"""
        ctx = {"finished": False, "questions_asked": 5}
        result = await classify_intent("我不想面了", ctx)
        assert result.get("end_interview") is True

    @pytest.mark.asyncio
    async def test_llm_returns_invalid_json(self, mock_llm_invalid):
        result = await classify_intent("hello", None)
        assert result["intent"] == "general"


class TestRouteDecision:
    def test_routes_resume_analyze(self):
        assert route_decision("resume_analyze") == "resume_agent"

    def test_routes_mock_interview(self):
        assert route_decision("mock_interview") == "interview_agent"

    def test_routes_general(self):
        assert route_decision("general") == "summary_agent"

    def test_routes_unknown_defaults_to_summary(self):
        assert route_decision("unknown_intent") == "summary_agent"

    def test_all_intents_have_routes(self):
        intents = ["resume_analyze", "match_position", "optimize_resume",
                   "mock_interview", "career_advice", "general"]
        routes = [route_decision(i) for i in intents]
        assert all(r is not None for r in routes)
        assert len(set(routes)) <= len(intents)  # some may share routes
