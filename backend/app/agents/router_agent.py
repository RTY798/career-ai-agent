"""Router Agent — 意图分类 + 条件路由（支持会话模式）"""

import json
import logging

from app.agents.llm_client import llm_client
from app.prompts.system_prompts import ROUTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


INTENT_LABELS = {
    "resume_analyze": "简历分析",
    "match_position": "人岗匹配",
    "optimize_resume": "简历优化",
    "mock_interview": "模拟面试",
    "career_advice": "职业咨询",
    "general": "一般对话",
}


async def classify_intent(user_message: str, interview_context: dict | None = None) -> dict:
    """分析用户意图，如果正在面试中则优先返回面试意图"""

    # ── 检查是否在面试模式中 ──
    if interview_context and not interview_context.get("finished"):
        # 检查用户是否想结束面试
        end_phrases = ["结束面试", "就这些", "没有问题了", "面试结束", "结束", "就到这里", "不想面了"]
        is_end = any(p in user_message for p in end_phrases)

        if is_end:
            logger.info("interview_end_requested")
            return {
                "intent": "mock_interview",
                "reason": "用户要求结束面试",
                "label": "模拟面试",
                "end_interview": True,
            }

        # 仍在面试中，继续面试流程
        logger.info("interview_ongoing, routing to interview_agent")
        return {
            "intent": "mock_interview",
            "reason": "正在进行模拟面试",
            "label": "模拟面试",
        }

    # ── 正常意图分类 ──
    response = await llm_client.complete(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        user_message=user_message,
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = response.get("content", "")
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"intent": "general", "reason": "JSON 解析失败，默认走 general"}

    intent = result.get("intent", "general")
    reason = result.get("reason", "")

    if intent not in INTENT_LABELS:
        intent = "general"

    logger.info("intent_classified", extra={"intent": intent, "reason": reason})

    return {
        "intent": intent,
        "reason": reason,
        "label": INTENT_LABELS.get(intent, "一般对话"),
    }


def route_decision(intent: str) -> str:
    """根据意图返回下一个节点名称"""
    routing = {
        "resume_analyze": "resume_agent",
        "match_position": "match_agent",
        "optimize_resume": "optimize_agent",
        "mock_interview": "interview_agent",
        "career_advice": "knowledge_agent",
        "general": "summary_agent",
    }
    return routing.get(intent, "summary_agent")
