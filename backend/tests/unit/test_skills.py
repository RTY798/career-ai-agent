"""TP0-1: BaseSkill JSON 解析韧性 + LLM 异常返回降级 (P0)"""

import json
import pytest
from app.skills import BaseSkill
from app.models.schemas import AnalyzeResponse


class MockSkill(BaseSkill):
    name = "test_skill"
    version = "1.0.0"

    async def execute(self, **kwargs):
        return {}


class TestParseJson:
    @pytest.fixture
    def skill(self):
        return MockSkill(None)

    def test_standard_json(self, skill):
        result = skill._parse_json('{"a": 1}')
        assert result == {"a": 1}

    def test_markdown_json_block(self, skill):
        result = skill._parse_json('```json\n{"a": 1}\n```')
        assert result == {"a": 1}

    def test_markdown_no_lang(self, skill):
        result = skill._parse_json('```\n{"a": 1}\n```')
        assert result == {"a": 1}

    def test_invalid_input_returns_none(self, skill):
        result = skill._parse_json("这不是 JSON")
        assert result is None

    def test_empty_string_returns_none(self, skill):
        result = skill._parse_json("")
        assert result is None

    def test_nested_json(self, skill):
        data = {"nested": {"list": [1, 2, 3], "key": "value"}}
        json_str = json.dumps(data)
        result = skill._parse_json(json_str)
        assert result == data

    def test_special_unicode(self, skill):
        data = {"text": "你好世界"}
        json_str = json.dumps(data, ensure_ascii=False)
        result = skill._parse_json(json_str)
        assert result == data


class TestResumeAnalysisSkill:
    @pytest.mark.asyncio
    async def test_execute_returns_dict(self, mock_llm, mock_agent_state):
        from app.skills.resume_skill import ResumeAnalysisSkill
        skill = ResumeAnalysisSkill(mock_llm)
        result = await skill.execute(
            resume_text="test",
            jd_text="test jd",
            role_type="ai",
        )
        assert isinstance(result, dict)
        assert "match_score" in result
        assert "skills_match" in result

    @pytest.mark.asyncio
    async def test_empty_resume_still_works(self, mock_llm):
        from app.skills.resume_skill import ResumeAnalysisSkill
        skill = ResumeAnalysisSkill(mock_llm)
        result = await skill.execute(resume_text="", jd_text="")
        assert isinstance(result, dict)
