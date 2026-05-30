"""人岗匹配技能包 — 语义匹配 + 量化打分 + 缺口分析"""

import logging

from app.skills import BaseSkill
from app.prompts.system_prompts import MATCH_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class MatchAnalysisSkill(BaseSkill):
    name = "match_analysis"
    version = "1.0.0"

    async def execute(self, resume_text: str, jd_text: str) -> dict:
        user_message = (
            f"=== 简历 ===\n{resume_text[:8000]}\n\n"
            f"=== 职位描述 ===\n{jd_text[:4000]}\n\n"
            f"请输出 JSON：\n"
            f'{{"match_score": 0-100, '
            f'"summary": "一句话匹配总结", '
            f'"skills_match": [{{"name":"...", "status":"matched", "importance":"required", "evidence":"..."}}], '
            f'"skills_gap": [{{"name":"...", "status":"missing/missing", "importance":"required/preferred"}}], '
            f'"suggestions": [{{"category":"content/format/keyword/experience", "text":"...", "priority":"high/medium/low"}}]}}'
        )

        response = await self.llm_client.complete(
            system_prompt=MATCH_SYSTEM_PROMPT,
            user_message=user_message,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = self._parse_json(response.get("content", ""))
        if not result:
            logger.error("match_skill_parse_failed")
            return {"match_score": 0, "summary": "分析失败", "skills_match": [], "skills_gap": [], "suggestions": []}

        return result
