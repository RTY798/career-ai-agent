"""Knowledge Agent — RAG 职业知识问答"""

import logging

from app.agents.llm_client import llm_client
from app.prompts.system_prompts import KNOWLEDGE_SYSTEM_PROMPT
from app.rag.hybrid_retriever import hybrid_retriever
from app.models.schemas import AgentState

logger = logging.getLogger(__name__)


async def run_knowledge_agent(state: AgentState) -> dict:
    """基于 RAG 检索的职业知识问答"""
    user_message = state.get("user_message", "")

    thought = {
        "agent": "知识检索",
        "status": "running",
        "input": user_message[:100],
    }
    state["thought_chain"].append(thought)

    # 混合检索知识库
    docs = hybrid_retriever.retrieve(user_message, top_k=3)
    state["retrieved_docs"] = docs

    # 构造上下文
    context = "\n\n".join(
        f"[文档 {i+1}] {d['content'][:500]}"
        for i, d in enumerate(docs)
    )

    thought["output"] = f"检索到 {len(docs)} 篇相关文档"
    thought["status"] = "completed"

    # 交给 summary 生成最终回答
    state["final_response"] = None
    return state


