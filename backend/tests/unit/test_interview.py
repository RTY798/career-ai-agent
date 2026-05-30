"""TP0-4: Interview Agent 全分支 (P0/smoke)"""

import pytest
from app.agents.interview_agent import run_interview_agent


class TestInterviewAgent:
    @pytest.mark.asyncio
    async def test_first_message_starts_interview(self, mock_llm, mock_agent_state):
        """首次"开始面试" → 出第一题"""
        state = mock_agent_state.copy()
        state["user_message"] = "开始面试"
        result = await run_interview_agent(state)
        ctx = result["interview_context"]
        assert ctx["questions_asked"] == 1
        assert ctx["finished"] is False
        assert result["final_response"] is not None
        assert "第 1 题" in result["final_response"]

    @pytest.mark.asyncio
    async def test_second_round_evaluates_and_continues(self, mock_llm, mock_agent_state):
        """第二轮回答 → 评估 + 出下一题"""
        state = mock_agent_state.copy()
        state["user_message"] = "我做了个AI客服系统，基于LangGraph"
        state["interview_context"] = {
            "history": [{"role": "assistant", "content": "**第 1 题**\n\n请介绍项目"}],
            "current_question": {"question": "请介绍项目", "category": "project", "difficulty": "medium"},
            "questions_asked": 1,
            "evaluations": [],
            "finished": False,
        }
        result = await run_interview_agent(state)
        ctx = result["interview_context"]
        assert ctx["questions_asked"] == 2
        assert len(ctx["evaluations"]) == 1
        assert result["final_response"] is not None

    @pytest.mark.asyncio
    async def test_end_interview_generates_report(self, mock_llm, mock_agent_state):
        """说"结束面试" → 生成报告"""
        state = mock_agent_state.copy()
        state["user_message"] = "结束面试"
        state["interview_context"] = {
            "history": [
                {"role": "assistant", "content": "**第 1 题**\n\n请介绍项目"},
                {"role": "user", "content": "我用了LangGraph"},
            ],
            "current_question": {"question": "请介绍项目", "category": "project"},
            "questions_asked": 3,
            "evaluations": [{"score": 75, "strengths": [], "weaknesses": [], "feedback": "不错"}],
            "finished": False,
        }
        result = await run_interview_agent(state)
        ctx = result["interview_context"]
        assert ctx["finished"] is True
        assert result["final_response"] is not None
        assert "总评" in result["final_response"]

    @pytest.mark.asyncio
    async def test_end_with_substring_triggers_report(self, mock_llm, mock_agent_state):
        """B3 regression: "我不想面了" → 结束"""
        state = mock_agent_state.copy()
        state["user_message"] = "我不想面了"
        state["interview_context"] = {
            "history": [{"role": "assistant", "content": "**第 1 题**\n\n请介绍项目"}],
            "current_question": {"question": "请介绍项目", "category": "project"},
            "questions_asked": 2,
            "evaluations": [],
            "finished": False,
        }
        result = await run_interview_agent(state)
        assert result["interview_context"]["finished"] is True

    @pytest.mark.asyncio
    async def test_end_on_first_message_starts_normally(self, mock_llm, mock_agent_state):
        """首次消息就"结束面试" → 正常出题（还没开始不能结束）"""
        state = mock_agent_state.copy()
        state["user_message"] = "结束面试"
        result = await run_interview_agent(state)
        ctx = result["interview_context"]
        # First message should start the interview, not end it
        assert ctx.get("finished") is not True

    @pytest.mark.asyncio
    async def test_llm_empty_question_uses_fallback(self, mock_llm):
        """LLM 返回空 → 用默认 fallback（通过 skill 测试验证）"""
        pass

    @pytest.mark.asyncio
    async def test_interview_keeps_history(self, mock_llm, mock_agent_state):
        """面试历史不丢失"""
        state = mock_agent_state.copy()
        state["user_message"] = "回答1"
        state["interview_context"] = {
            "history": [
                {"role": "assistant", "content": "**第 1 题**\n\n请介绍项目"},
            ],
            "current_question": {"question": "请介绍项目", "category": "project", "difficulty": "medium"},
            "questions_asked": 1,
            "evaluations": [],
            "finished": False,
        }
        result = await run_interview_agent(state)
        ctx = result["interview_context"]
        assert len(ctx["history"]) >= 3  # 初始 + 回答 + 下一题
