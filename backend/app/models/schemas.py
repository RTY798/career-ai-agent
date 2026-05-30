from __future__ import annotations

from typing import Optional, TypedDict

from pydantic import BaseModel, Field


# ── Agent State ──

class AgentState(TypedDict):
    user_message: str
    messages: list[dict]
    intent: Optional[str]
    resume_text: Optional[str]
    jd_text: Optional[str]
    parsed_resume: Optional[dict]
    match_result: Optional[dict]
    optimize_report: Optional[dict]
    retrieved_docs: list[dict]
    interview_context: Optional[dict]
    final_response: Optional[str]
    thought_chain: list[dict]
    error: Optional[str]


# ── API Schemas ──

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    resume: Optional[str] = Field(None, max_length=50000)   # B5 fix
    jd: Optional[str] = Field(None, max_length=50000)       # B5 fix
    conversation_id: Optional[str] = None


class SSEEvent(BaseModel):
    event: str  # thought | message | report | ticket | error | done
    data: dict


# ── Analysis Results ──

class SkillItem(BaseModel):
    name: str
    status: str  # matched | missing | partial
    importance: str  # required | preferred
    evidence: Optional[str] = None


class Suggestion(BaseModel):
    category: str  # content | format | keyword | experience
    text: str
    priority: str  # high | medium | low


class InterviewQuestion(BaseModel):
    question: str
    category: str  # technical | behavioral | project | behavioral
    rationale: Optional[str] = None


class AnalyzeResponse(BaseModel):
    analysis_id: str
    match_score: int
    summary: str
    skills_match: list[SkillItem]
    skills_gap: list[SkillItem]
    suggestions: list[Suggestion]
    interview_questions: list[InterviewQuestion]


class OptimizeItem(BaseModel):
    section_index: int
    original_text: str
    optimized_text: str
    issue_type: str  # weak_verb | no_quantification | weak_wording | missing_skill | format_inconsistency
    reason: str
    expected_impact: str  # high | medium | low


class OptimizeReport(BaseModel):
    original_resume: str
    optimized_resume: str
    changes: list[OptimizeItem]
    total_improvement: int  # estimated match score improvement


class InterviewReport(BaseModel):
    overall_score: int
    dimension_scores: dict
    strengths: list[str]
    weaknesses: list[str]
    question_reviews: list[dict]
    improvement_plan: list[str]


class MatchResult(BaseModel):
    match_score: int
    skills_match: list[SkillItem]
    skills_gap: list[SkillItem]
    suggestions: list[Suggestion]


__all__ = [
    "AgentState", "ChatRequest", "SSEEvent",
    "SkillItem", "Suggestion", "InterviewQuestion", "AnalyzeResponse",
    "OptimizeItem", "OptimizeReport", "InterviewReport", "MatchResult",
]
