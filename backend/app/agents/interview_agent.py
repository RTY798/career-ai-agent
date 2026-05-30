"""Interview Agent — 多轮模拟面试 + 报告生成（持续进行，用户控制结束）"""

import logging

from app.agents.llm_client import llm_client
from app.skills.interview_skill import InterviewSkill
from app.models.schemas import AgentState

logger = logging.getLogger(__name__)

interview_skill = InterviewSkill(llm_client)


async def run_interview_agent(state: AgentState) -> dict:
    """多轮模拟面试：持续进行，直到用户说结束"""
    user_message = state.get("user_message", "")
    resume_text = state.get("resume_text", "")
    jd_text = state.get("jd_text", "")
    interview_ctx = state.get("interview_context") or {}
    end_requested = (state.get("interview_context") or {}).get("finished")

    thought = {
        "agent": "模拟面试",
        "status": "running",
        "input": user_message[:100],
    }
    state["thought_chain"].append(thought)

    history = interview_ctx.get("history", [])
    is_first_message = not history
    end_phrases = ["结束面试", "结束", "就这些", "就到这里", "没有问题了", "不想面了"]
    is_end = end_requested or any(p in user_message for p in end_phrases)  # B3 fix: substring match

    if is_end and not is_first_message:
        # 用户主动结束 → 生成面试报告
        state["final_response"] = await _finish_interview(state, interview_ctx)
        thought["status"] = "completed"
        thought["output"] = f"面试结束，生成报告"
        return state

    if is_first_message or user_message in ["开始面试", "模拟面试", "开始"]:
        # 开始新面试 — 出第一道题
        question = await interview_skill.generate_question(resume_text, jd_text, [])
        response_text = _format_question(question, 1)
        interview_ctx = {
            "history": [{"role": "assistant", "content": response_text}],
            "current_question": question,
            "questions_asked": 1,
            "evaluations": [],
            "finished": False,
        }
        thought["output"] = f"第1题 ({question.get('category', 'general')})"

    else:
        # 继续面试 — 评估上题回答 + 出下一题
        last_question = interview_ctx.get("current_question", {})
        evaluation = await interview_skill.evaluate_answer(
            last_question.get("question", ""), user_message, interview_ctx,
        )
        evaluations = interview_ctx.get("evaluations", [])
        evaluations.append(evaluation)
        history.append({"role": "user", "content": user_message})

        questions_asked = interview_ctx.get("questions_asked", 0) + 1
        next_question = await interview_skill.generate_question(resume_text, jd_text, history)
        response_text = _format_question(next_question, questions_asked, evaluation)

        interview_ctx["current_question"] = next_question
        interview_ctx["questions_asked"] = questions_asked
        interview_ctx["evaluations"] = evaluations
        interview_ctx["finished"] = False

        thought["output"] = f"第{questions_asked}题 ({next_question.get('category', 'general')})"

        # 每5题提示一次可结束
        if questions_asked % 5 == 0:
            response_text += "\n\n---\n💡 如果想结束面试，请输入「结束面试」"

    # 更新历史
    history.append({"role": "assistant", "content": response_text})
    interview_ctx["history"] = history
    state["interview_context"] = interview_ctx
    state["final_response"] = response_text
    thought["status"] = "completed"

    return state


async def _finish_interview(state: AgentState, ctx: dict) -> str:
    """生成面试报告"""
    report = await interview_skill.generate_report(ctx.get("history", []))
    ctx["report"] = report
    ctx["finished"] = True
    state["interview_context"] = ctx
    state["parsed_resume"] = state.get("parsed_resume") or {}
    if isinstance(state["parsed_resume"], dict):
        state["parsed_resume"]["interview_report"] = report

    dims = report.get("dimension_scores", {})
    lines = ["## 📋 面试结束！\n"]
    lines.append(f"**总评：{report.get('overall_score', 0)}/100**\n")
    if dims:
        lines.append("**各维度得分：**")
        for k, v in dims.items():
            bars = "█" * (v // 10) + "░" * (10 - v // 10)
            lines.append(f"- {k}: {v}分 {bars}")
    strengths = report.get("strengths", [])
    if strengths:
        lines.append("\n**✅ 优势：**")
        for s in strengths:
            lines.append(f"- {s}")
    weaknesses = report.get("weaknesses", [])
    if weaknesses:
        lines.append("\n**⚠️ 待改进：**")
        for w in weaknesses:
            lines.append(f"- {w}")
    plan = report.get("improvement_plan", [])
    if plan:
        lines.append("\n**📌 提升计划：**")
        for p in plan:
            lines.append(f"- {p}")
    lines.append("\n---\n还有什么需要我帮忙的吗？")
    return "\n".join(lines)


def _format_question(question: dict, num: int, evaluation: dict | None = None) -> str:
    """格式化面试题"""
    lines = []
    if evaluation:
        score = evaluation.get("score", 0)
        lines.append(f"**回答评分：{score}/100**")
        fb = evaluation.get("feedback", "")
        if fb:
            lines.append(f"> {fb}\n")

    cat_label = {"technical": "💻 技术", "behavioral": "👤 行为", "project": "📁 项目"}
    cat = cat_label.get(question.get("category", ""), "💡 通用")
    lines.append(f"**第 {num} 题** ({cat})")
    lines.append("")
    lines.append(question.get("question", "请介绍一下你自己。"))
    lines.append("")
    lines.append("---\n输入你的回答，或输入「结束面试」结束。")
    return "\n".join(lines)
