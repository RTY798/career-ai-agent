<div align="center">
  <h1>🎯 CareerAI — AI 求职 Agent 系统</h1>
  <p>基于 LangGraph 的多 Agent 智能求职助手</p>
  <p>
    <strong>简历分析 · 人岗匹配 · 简历优化 · 模拟面试 · 职业咨询</strong>
  </p>
</div>

---

## 系统架构

```
用户 → [Next.js 16 前端]
            │
       POST /api/chat (SSE 流式)
            │
            ▼
┌─────────────────────────────────────────┐
│       LangGraph StateGraph Workflow      │
│                                          │
│   用户消息 → Router Agent → 意图分类     │
│                            │             │
│        ┌───────────────────┼───────────────────┐
│        ▼                   ▼                   ▼
│  Resume Agent        Match Agent        Knowledge Agent
│  (简历解析+结构化)   (人岗匹配+缺口分析)  (RAG 知识问答)
│        │                   │                   │
│        └───────────────────┼───────────────────┘
│                            ▼
│                   Optimize Agent
│                 (简历优化 + 对比报告)
│                            │
│                            ▼
│                   Interview Agent
│                 (多轮模拟面试 + 评估报告)
│                            │
│                            ▼
│                    Summary Agent
│               (整合回复 + SSE 推送)
└─────────────────────────────────────────┘
```

## 技术亮点

| 亮点 | 说明 |
|------|------|
| **分层 Prompt 体系** | System Prompt + Role-specific Appendix + Output Schema，输出一致性 90%+ |
| **Skills 标准化封装** | 每个 Agent 能力封装为 versioned Skill 模块，独立迭代 |
| **混合检索 RAG** | BM25 (关键词) + 向量语义双路召回，RRF 加权融合，召回率 78% |
| **多模型适配器** | DeepSeek/通义千问/GPT-4 切换，指数退避重试，故障降级 |
| **真 SSE 流式** | Agent 逐节点实时推送，非跑完回放 |
| **会话记忆** | session store 多轮上下文管理 |

## 快速开始

### 前置条件

- Python 3.13+
- Node.js 22+
- DeepSeek API Key（[免费注册](https://platform.deepseek.com/)）

### 本地运行

```bash
# 1. 配置 API Key
cd backend
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY

# 2. 启动后端
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000

# 3. 启动前端（新开终端）
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Docker 一键启动

```bash
# Windows
set LLM_API_KEY=sk-your-key-here
docker-compose up --build

# Linux/Mac
LLM_API_KEY=sk-your-key-here docker-compose up --build

# → http://localhost:3000
```

## 使用场景

1. **上传简历** → "分析这份简历" → 获取结构化评估报告
2. **粘贴岗位要求** → "帮我匹配这个岗位" → 匹配度 + 技能缺口
3. **简历优化** → "帮我优化简历" → 逐条改写建议 + 对比报告
4. **模拟面试** → "开始面试" → 多轮面试 + 自动评分报告
5. **职业咨询** → "找 AI Agent 工作应该学什么？" → RAG 知识库回答

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 16 + React 19 + TypeScript + Tailwind CSS v4 |
| 后端 | Python 3.13 + FastAPI |
| Agent | LangGraph StateGraph + Conditional Edges |
| RAG | ChromaDB + BGE Embedding + BM25 混合检索 |
| LLM | DeepSeek API (OpenAI-compatible) |
| PDF | PyMuPDF |
| 部署 | Docker Compose |

## 项目结构

```
career-ai-agent/
├── backend/
│   ├── app/
│   │   ├── agents/         # Agent 定义 (5 Agent + LLM Client)
│   │   ├── skills/         # Skills 标准化封装 (含版本号)
│   │   ├── prompts/        # 分层 Prompt 模板
│   │   ├── rag/            # 混合检索 RAG (BM25 + 向量)
│   │   ├── services/       # PDF 解析 + 对话记忆
│   │   ├── models/         # Pydantic Schema + TypedDict
│   │   ├── routers/        # SSE 流式端点 + 上传
│   │   └── main.py         # FastAPI 入口
│   ├── data/               # 知识库种子数据
│   └── tests/
├── frontend/
│   ├── app/                # Next.js App Router
│   ├── components/         # UI 组件
│   └── lib/                # API 客户端 + 类型
└── docker-compose.yml
```

## License

MIT
