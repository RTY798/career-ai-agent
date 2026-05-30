"""面试评估技能包 — 多轮面试 + 自动报告生成"""

import json
import logging

from app.skills import BaseSkill
from app.prompts.system_prompts import INTERVIEW_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class InterviewSkill(BaseSkill):
    name = "interview"
    version = "1.0.0"

    async def execute(self, **kwargs) -> dict:
        """实现抽象方法，委托给具体方法"""
        action = kwargs.get("action", "question")
        if action == "question":
            return await self.generate_question(
                kwargs.get("resume_text", ""),
                kwargs.get("jd_text", ""),
                kwargs.get("history", []),
            )
        elif action == "evaluate":
            return await self.evaluate_answer(
                kwargs.get("question", ""),
                kwargs.get("answer", ""),
                kwargs.get("context", {}),
            )
        elif action == "report":
            return await self.generate_report(kwargs.get("history", []))
        return {"question": "请介绍一下你自己。"}

    async def generate_question(
        self, resume_text: str, jd_text: str, history: list[dict]
    ) -> dict:
        """基于简历和JD生成下一道面试题"""
        history_context = ""
        if history:
            history_context = "\n".join(
                f"面试官: {h['content']}" if h["role"] == "assistant" else f"候选人: {h['content']}"
                for h in history[-6:]
            )

        user_message = (
            f"=== 简历 ===\n{resume_text[:4000]}\n\n"
            f"=== 职位要求 ===\n{jd_text[:2000] if jd_text else '无'}\n\n"
            f"=== 已进行的对话 ===\n{history_context or '尚未开始'}\n\n"
            f"输出 JSON：{{'question': '...', 'category': 'technical|behavioral|project', "
            f"'difficulty': 'easy|medium|hard', 'expected_points': ['...']}}"
        )

        response = await self.llm_client.complete(
            system_prompt=INTERVIEW_SYSTEM_PROMPT,
            user_message=user_message,
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        result = self._parse_json(response.get("content", ""))
        if not result:
            result = {"question": "请介绍一下你最近做的一个项目？", "category": "project", "difficulty": "medium"}

        logger.info("interview_question_generated", extra={"category": result.get("category")})
        return result

    async def evaluate_answer(self, question: str, answer: str, context: dict) -> dict:
        """评估候选人回答"""
        user_message = (
            f"=== 面试题 ===\n{question}\n\n"
            f"=== 候选人回答 ===\n{answer}\n\n"
            f"输出 JSON：\n"
            f'{{"score": 0-100, "strengths": ["..."], "weaknesses": ["..."], '
            f'"feedback": "具体反馈", "reference_approach": "参考答案思路"}}'
        )

        response = await self.llm_client.complete(
            system_prompt=INTERVIEW_SYSTEM_PROMPT,
            user_message=user_message,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = self._parse_json(response.get("content", ""))
        if not result:
            result = {"score": 60, "strengths": [], "weaknesses": ["无法评估"], "feedback": "评估失败", "reference_approach": ""}

        return result

    async def generate_report(self, history: list[dict]) -> dict:
        """面试结束自动生成结构化报告"""
        history_text = "\n".join(
            f"{m['role']}: {m['content'][:200]}"
            for m in history
        )

        user_message = (
            f"=== 面试记录 ===\n{history_text}\n\n"
            f"输出 JSON 面试报告：\n"
            f'{{"overall_score": 0-100, '
            f'"dimension_scores": {{"technical": 0-100, "project": 0-100, "behavioral": 0-100, "communication": 0-100}}, '
            f'"strengths": ["..."], "weaknesses": ["..."], '
            f'"improvement_plan": ["..."], '
            f'"question_reviews": [{{"question": "...", "score": 0-100, "feedback": "..."}}]}}'
        )

        response = await self.llm_client.complete(
            system_prompt="你是一位资深面试评估专家，基于面试记录生成详细评估报告。",
            user_message=user_message,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = self._parse_json(response.get("content", ""))
        if not result:
            result = {"overall_score": 0, "dimension_scores": {}, "strengths": [], "weaknesses": [],
                     "improvement_plan": [], "question_reviews": []}

        return result
