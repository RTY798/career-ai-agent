"""FastAPI 应用入口"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, health, upload

# ── 日志配置 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# ── 应用 ──
app = FastAPI(
    title="CareerAI Agent — AI 求职 Agent 系统",
    version="1.0.0",
    description="基于 LangGraph 的多 Agent 智能求职系统",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 路由 ──
app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")


@app.on_event("startup")
async def startup():
    from app.rag.hybrid_retriever import hybrid_retriever
    from app.rag.vector_store import vector_store

    # 如果知识库为空，初始化种子数据
    if vector_store.count() == 0:
        logger.info("seeding knowledge base...")
        from app.data.seed import seed_knowledge_base
        seed_knowledge_base()
        # 重建 BM25 索引
        all_docs = [d["content"] for d in vector_store.similarity_search("", k=100)]
        if all_docs:
            hybrid_retriever.rebuild_index(all_docs)
        logger.info("knowledge base seeded")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
    )
