"""简历优化技能包 — 空洞动词/缺量化/措辞弱/技能缺失/格式不一致检测"""

import logging

from app.skills import BaseSkill
from app.prompts.system_prompts import OPTIMIZE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ResumeOptimizeSkill(BaseSkill):
    name = "resume_optimize"
    version = "1.0.0"

    async def execute(self, resume_text: str, match_result: dict | None = None) -> dict:
        match_context = ""
        if match_result:
            gap_names = [g.get("name", "") for g in match_result.get("skills_gap", [])]
            match_context = f"\n需要补充的关键技能：{', '.join(gap_names[:5])}"

        user_message = (
            f"=== 简历原文 ===\n{resume_text[:8000]}\n\n"
            f"=== 优化指令 ==={match_context}\n\n"
            f"请按段落分析，对每个需要修改的位置输出：\n"
            f'[{{"section_index": 0, "original_text": "...", "optimized_text": "...", '
            f'"issue_type": "weak_verb|no_quantification|weak_wording|missing_skill|format_inconsistency", '
            f'"reason": "...", "expected_impact": "high|medium|low"}}]\n\n'
            f"最后给出优化后的完整简历文本。"
        )

        response = await self.llm_client.complete(
            system_prompt=OPTIMIZE_SYSTEM_PROMPT,
            user_message=user_message,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        result = self._parse_json(response.get("content", ""))
        if not result:
            return {"changes": [], "optimized_resume": resume_text, "total_improvement": 0}

        return result
