"""Summary Agent — 整合所有 Agent 输出，生成最终回复"""

import json
import logging

from app.agents.llm_client import llm_client
from app.prompts.system_prompts import SUMMARY_SYSTEM_PROMPT, KNOWLEDGE_SYSTEM_PROMPT
from app.models.schemas import AgentState

logger = logging.getLogger(__name__)


async def run_summary_agent(state: AgentState) -> dict:
    """整合多 Agent 输出为友好回复"""
    intent = state.get("intent", "general")
    user_message = state.get("user_message", "")
    parsed_resume = state.get("parsed_resume")
    match_result = state.get("match_result")
    optimize_report = state.get("optimize_report")
    retrieved_docs = state.get("retrieved_docs", [])
    interview_ctx = state.get("interview_context")

    thought = {
        "agent": "整合回复",
        "status": "running",
        "input": f"意图: {intent}",
    }
    state["thought_chain"].append(thought)

    # 根据意图直接构造回复
    response = await _build_response(
        intent, user_message, parsed_resume, match_result,
        optimize_report, retrieved_docs, interview_ctx,
    )

    state["final_response"] = response
    thought["status"] = "completed"
    thought["output"] = f"回复已生成 ({len(response)}字)"
    return state


async def _build_response(
    intent: str,
    user_message: str,
    parsed_resume: dict | None,
    match_result: dict | None,
    optimize_report: dict | None,
    retrieved_docs: list[dict],
    interview_ctx: dict | None,
) -> str:
    """根据意图和 Agent 输出构造最终回复"""

    if intent == "resume_analyze" and parsed_resume:
        score = parsed_resume.get("match_score", 0)
        skills = parsed_resume.get("skills_match", [])
        gaps = parsed_resume.get("skills_gap", [])
        suggestions = parsed_resume.get("suggestions", [])
        questions = parsed_resume.get("interview_questions", [])

        lines = [f"## 📊 简历分析报告\n"]
        lines.append(f"**匹配度评分：{score}/100**\n")
        lines.append(f"_{parsed_resume.get('summary', '')}_\n")

        if skills:
            lines.append("### ✅ 已匹配技能")
            for s in skills[:8]:
                lines.append(f"- **{s['name']}** ({s['importance']})")
        if gaps:
            lines.append("\n### ❌ 技能缺口")
            for g in gaps[:6]:
                lines.append(f"- **{g['name']}** ({g['importance']})")
        if suggestions:
            lines.append("\n### 💡 改进建议")
            for s in suggestions[:5]:
                lines.append(f"- [{s['priority']}] {s['text']}")
        if questions:
            lines.append("\n### 🔍 面试预判")
            for q in questions[:3]:
                lines.append(f"- {q['question']}")

        return "\n".join(lines)

    if intent == "match_position" and match_result:
        score = match_result.get("match_score", 0)
        lines = [f"## 🎯 人岗匹配结果\n"]
        lines.append(f"**匹配度：{score}/100**\n")
        lines.append(f"_{match_result.get('summary', '')}_\n")

        skills = match_result.get("skills_match", [])
        if skills:
            lines.append("### ✅ 匹配项")
            for s in skills[:6]:
                lines.append(f"- {s['name']} ({s.get('evidence', '匹配')})")

        gaps = match_result.get("skills_gap", [])
        if gaps:
            lines.append("\n### ⚠️ 缺口项")
            for g in gaps[:6]:
                lines.append(f"- {g['name']} ({'必需' if g.get('importance') == 'required' else '加分'})")

        sugs = match_result.get("suggestions", [])
        if sugs:
            lines.append("\n### 💡 建议")
            for s in sugs[:4]:
                lines.append(f"- {s['text']}")

        lines.append("\n---\n需要我帮你优化简历，或者针对这个岗位进行模拟面试吗？")
        return "\n".join(lines)

    if intent == "optimize_resume" and optimize_report:
        changes = optimize_report.get("changes", [])
        optimized = optimize_report.get("optimized_resume", "")

        lines = [f"## ✏️ 简历优化建议\n"]
        lines.append(f"发现 **{len(changes)}** 处可优化点：\n")

        issue_labels = {
            "weak_verb": "空洞动词",
            "no_quantification": "缺量化",
            "weak_wording": "措辞弱",
            "missing_skill": "技能缺失",
            "format_inconsistency": "格式不一致",
        }
        for c in changes[:8]:
            label = issue_labels.get(c.get("issue_type", ""), c.get("issue_type"))
            impact = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(c.get("expected_impact", ""), "")
            lines.append(f"{impact} **{label}**：")
            lines.append(f"  - 原文：{c.get('original_text', '')[:100]}")
            lines.append(f"  - 修改：{c.get('optimized_text', '')[:100]}")
            lines.append(f"  - 理由：{c.get('reason', '')}")

        lines.append("\n---\n需要我直接输出优化后的完整简历文本吗？")
        return "\n".join(lines)

    if intent == "career_advice" and retrieved_docs:
        docs_context = "\n\n".join(
            f"[知识 {i+1}] {d['content'][:600]}"
            for i, d in enumerate(retrieved_docs[:3])
        )
        response = await llm_client.complete(
            system_prompt=KNOWLEDGE_SYSTEM_PROMPT,
            user_message=(
                f"用户问题：{user_message}\n\n"
                f"参考知识：\n{docs_context}\n\n"
                f"请基于参考知识回答，如果知识不够请明确说明。"
            ),
            temperature=0.5,
        )
        return response.get("content", "抱歉，无法回答该问题。")

    if interview_ctx and interview_ctx.get("finished"):
        report = interview_ctx.get("report", {})
        lines = [f"## 📋 面试评估报告\n"]
        dims = report.get("dimension_scores", {})
        if dims:
            lines.append("**各维度得分：**")
            for k, v in dims.items():
                bars = "█" * (v // 10) + "░" * (10 - v // 10)
                lines.append(f"- {k}: {v}分 {bars}")

        lines.append(f"\n**总分：{report.get('overall_score', 0)}/100**\n")

        strengths = report.get("strengths", [])
        if strengths:
            lines.append("**优势：**")
            for s in strengths:
                lines.append(f"- ✅ {s}")

        weaknesses = report.get("weaknesses", [])
        if weaknesses:
            lines.append("\n**待改进：**")
            for w in weaknesses:
                lines.append(f"- ⚠️ {w}")

        plan = report.get("improvement_plan", [])
        if plan:
            lines.append("\n**提升计划：**")
            for p in plan:
                lines.append(f"- 📌 {p}")

        return "\n".join(lines)

    # 默认：general 或未匹配
    response = await llm_client.complete(
        system_prompt=SUMMARY_SYSTEM_PROMPT,
        user_message=user_message,
        temperature=0.7,
    )
    return response.get("content", "你好！我是 CareerAI 求职助手，你可以上传简历让我分析，或告诉我你想做什么。")
