"""共享 fixtures：mock LLM + mock ChromaDB + 测试数据"""

import pytest


# ── Mock Response Templates ──

MOCK_RESUME_ANALYSIS = {
    "match_score": 75,
    "summary": "候选人技术栈匹配度良好",
    "skills_match": [
        {"name": "Python", "status": "matched", "importance": "required", "evidence": "多个项目使用"},
        {"name": "LangGraph", "status": "matched", "importance": "required", "evidence": "客服Agent项目"},
    ],
    "skills_gap": [
        {"name": "Kubernetes", "status": "missing", "importance": "preferred"},
        {"name": "Redis", "status": "missing", "importance": "preferred"},
    ],
    "suggestions": [{"category": "content", "text": "补充Docker经验", "priority": "high"}],
    "interview_questions": [{"question": "请描述LangGraph状态图的工作原理", "category": "technical", "rationale": "测试Agent框架理解"}],
}

MOCK_MATCH_RESULT = {
    "match_score": 78,
    "summary": "简历与JD匹配度良好",
    "skills_match": [{"name": "Python", "status": "matched", "importance": "required", "evidence": "项目经验"}],
    "skills_gap": [{"name": "Docker", "status": "missing", "importance": "preferred"}],
    "suggestions": [{"category": "keyword", "text": "补充Docker技能", "priority": "high"}],
}

MOCK_OPTIMIZE_REPORT = {
    "changes": [
        {"section_index": 0, "original_text": "负责开发", "optimized_text": "设计并实现了",
         "issue_type": "weak_verb", "reason": "空洞动词替换", "expected_impact": "high"},
    ],
    "optimized_resume": "设计并实现了AI客服系统...",
    "total_improvement": 5,
}

MOCK_INTERVIEW_QUESTION = {
    "question": "请介绍一下你最近完成的一个项目？",
    "category": "project",
    "difficulty": "medium",
    "expected_points": ["项目背景", "技术栈", "个人贡献"],
}

MOCK_INTERVIEW_EVALUATION = {
    "score": 75,
    "strengths": ["技术理解准确", "表达清晰"],
    "weaknesses": ["缺少量化成果"],
    "feedback": "建议补充具体数据",
    "reference_approach": "从背景->方案->成果三个层次展开",
}

MOCK_INTERVIEW_REPORT = {
    "overall_score": 72,
    "dimension_scores": {"technical": 70, "project": 75, "behavioral": 70, "communication": 73},
    "strengths": ["技术基础扎实"],
    "weaknesses": ["项目经验不够深入"],
    "improvement_plan": ["多准备系统设计题"],
    "question_reviews": [{"question": "请介绍项目", "score": 75, "feedback": "表达清晰但缺数据"}],
}

MOCK_GENERAL_REPLY = "你好！我是 CareerAI 求职助手，有什么可以帮你的？"


# ── Mock LLM Response ──

class MockLLMResponse:
    """模拟 LLM 返回，各类意图返回对应预设数据"""

    def __init__(self, content: str = "", model: str = "mock", latency_ms: int = 10):
        self.content = content
        self.model = model
        self.latency_ms = latency_ms

    def get(self, key: str, default=None):
        return {"content": self.content, "usage": {"total_tokens": 50},
                "model": self.model, "latency_ms": self.latency_ms}.get(key, default)


class MockLLMClient:
    """模拟 LLMClientManager，不调用真实 API"""

    def __init__(self, mode: str = "normal"):
        self.mode = mode
        self.last_system_prompt = ""
        self.last_user_message = ""
        self.call_count = 0

    async def complete(self, system_prompt: str = "", user_message: str = "", **kwargs) -> dict:
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        self.call_count += 1

        content = self._get_content(system_prompt, user_message)
        return {
            "content": content,
            "usage": {"total_tokens": 50},
            "model": "mock",
            "latency_ms": 10,
        }

    def _get_content(self, system_prompt: str, user_message: str) -> str:
        if self.mode == "empty":
            return ""
        if self.mode == "invalid_json":
            return "这不是JSON"

        import json
        # 根据 system prompt 判断意图
        if "路由助手" in system_prompt:
            return '{"intent": "general", "reason": "mock"}'
        if "招聘专家" in system_prompt:
            return json.dumps(MOCK_RESUME_ANALYSIS, ensure_ascii=False)
        if "人岗匹配" in system_prompt:
            return json.dumps(MOCK_MATCH_RESULT, ensure_ascii=False)
        if "简历优化" in system_prompt:
            return json.dumps(MOCK_OPTIMIZE_REPORT, ensure_ascii=False)
        if "面试官" in system_prompt or "面试评估" in system_prompt:
            if "记录" in user_message or "记录" in system_prompt:
                return json.dumps(MOCK_INTERVIEW_REPORT, ensure_ascii=False)
            if "评估" in system_prompt or ("score" in user_message):
                return json.dumps(MOCK_INTERVIEW_EVALUATION, ensure_ascii=False)
            return json.dumps(MOCK_INTERVIEW_QUESTION, ensure_ascii=False)
        if "总结助手" in system_prompt:
            return MOCK_GENERAL_REPLY

        return MOCK_GENERAL_REPLY


# ── Fixtures ──

@pytest.fixture
def mock_llm():
    return MockLLMClient("normal")


@pytest.fixture
def mock_llm_empty():
    return MockLLMClient("empty")


@pytest.fixture
def mock_llm_invalid():
    return MockLLMClient("invalid_json")


@pytest.fixture
def mock_agent_state():
    """基础 AgentState fixture"""
    return {
        "user_message": "hello",
        "messages": [],
        "intent": None,
        "resume_text": "欧阳博亚，本科，熟悉Python、LangGraph",
        "jd_text": "AI Agent开发工程师，要求Python、LangGraph",
        "parsed_resume": None,
        "match_result": None,
        "optimize_report": None,
        "retrieved_docs": [],
        "interview_context": None,
        "final_response": None,
        "thought_chain": [],
        "error": None,
    }


@pytest.fixture
def mock_agent_state_with_history(mock_agent_state):
    """带历史消息的 AgentState"""
    state = mock_agent_state.copy()
    state["messages"] = [
        {"role": "user", "content": "我叫张三", "timestamp": 1000},
        {"role": "assistant", "content": "你好张三！", "timestamp": 1001},
    ]
    return state
