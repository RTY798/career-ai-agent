"""简历分析技能包 — 分层 Prompt + 结构化输出"""

import logging

from app.skills import BaseSkill
from app.prompts.system_prompts import (
    RESUME_SYSTEM_PROMPT,
    AI_ROLE_APPENDIX,
    TECH_ROLE_APPENDIX,
    PRODUCT_ROLE_APPENDIX,
)

logger = logging.getLogger(__name__)


class ResumeAnalysisSkill(BaseSkill):
    name = "resume_analysis"
    version = "2.1.0"

    async def execute(
        self,
        resume_text: str,
        jd_text: str = "",
        role_type: str = "ai",
    ) -> dict:
        """执行简历分析，返回结构化结果"""
        # 动态注入 Role-specific Appendix
        appendix_map = {
            "tech": TECH_ROLE_APPENDIX,
            "product": PRODUCT_ROLE_APPENDIX,
            "ai": AI_ROLE_APPENDIX,
        }
        appendix = appendix_map.get(role_type, AI_ROLE_APPENDIX)

        system_prompt = f"{RESUME_SYSTEM_PROMPT}\n\n{appendix}"

        user_message = (
            f"=== 简历内容 ===\n{resume_text[:8000]}\n\n"
            f"=== 职位描述 ===\n{jd_text[:4000] if jd_text else '无'}\n\n"
            f"请严格按照 JSON 格式输出分析结果：\n"
            f'{{"match_score": 0-100, "summary": "...", '
            f'"skills_match": [{{"name":"...", "status":"matched", "importance":"required", "evidence":"..."}}], '
            f'"skills_gap": [{{"name":"...", "status":"missing", "importance":"required"}}], '
            f'"suggestions": [{{"category":"content", "text":"...", "priority":"high"}}], '
            f'"interview_questions": [{{"question":"...", "category":"technical", "rationale":"..."}}]}}'
        )

        response = await self.llm_client.complete(
            system_prompt=system_prompt,
            user_message=user_message,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = self._parse_json(response.get("content", ""))
        if not result:
            logger.error("resume_skill_parse_failed", extra={"raw": response.get("content")})
            return self._default_result()

        logger.info(
            "skill_executed",
            extra={
                "skill": self.name,
                "version": self.version,
                "tokens": response.get("usage", {}).get("total_tokens"),
            },
        )

        return result

    def _default_result(self) -> dict:
        return {
            "match_score": 0,
            "summary": "分析失败，请重试。",
            "skills_match": [],
            "skills_gap": [],
            "suggestions": [],
            "interview_questions": [],
        }
