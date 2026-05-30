<div align="center">
  <h1>🎯 CareerAI</h1>
  <p><strong>AI 求职 Agent 系统 — 基于 LangGraph 的多 Agent 协作平台</strong></p>
  <p>
    <a href="https://github.com/RTY798/career-ai-agent/blob/master/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
    </a>
    <img src="https://img.shields.io/badge/python-3.13+-orange" alt="Python 3.13+">
    <img src="https://img.shields.io/badge/node-22+-green" alt="Node 22+">
    <img src="https://img.shields.io/badge/status-alpha-yellow" alt="Status">
  </p>
  <br>
</div>

---

## 📖 简介

CareerAI 是一个开源的 AI 求职 Agent 系统。上传简历 → AI 自动分析匹配度 → 优化简历内容 → 模拟面试练习 → 拿到 offer。

**三种角色使用：**

| 角色 | 能做什么 |
|------|---------|
| 🎓 **求职者** | 上传简历 → 分析匹配度 → 优化简历 → 模拟面试 → 职业咨询 |
| 👔 **HR 招聘官** | 生成面试题 → 评估候选人 |
| 🧑‍💻 **开发者** | 查看系统架构 → 调试 API → 监控性能 → 二次开发 |

**六大功能：**

- 📄 **简历分析** — 上传 PDF，自动解析并打出匹配度评分
- 🎯 **人岗匹配** — 对比简历与职位描述，量化技能缺口
- ✏️ **简历优化** — 检测空洞动词、缺量化，逐条改写
- 🎤 **模拟面试** — 多轮问答 + 自动评分 + 完整评估报告
- 💡 **职业咨询** — 基于 RAG 知识库回答求职问题
- 🔌 **API 调试** — 可视化接口面板，实时查看响应

---

## 🚀 三分钟快速上手

### 第一步：获取 API Key

前往 [DeepSeek 开放平台](https://platform.deepseek.com/) → 免费注册 → 创建 API Key → 复制。

> 不需要其他任何配置，只需要这一个 Key。

### 第二步：克隆并配置

```bash
git clone https://github.com/RTY798/career-ai-agent.git
cd career-ai-agent/backend
cp .env.example .env
```

打开 `.env`，将 `LLM_API_KEY=` 后面粘贴你的 Key：

```ini
LLM_API_KEY=sk-你的key粘贴到这里
```

### 第三步：启动

#### 方式一：一键启动（推荐）

```bash
# Windows
set LLM_API_KEY=sk-你的key
docker-compose up --build

# Linux / Mac
LLM_API_KEY=sk-你的key docker-compose up --build
```

浏览器打开 **http://localhost:3000**。

#### 方式二：本地手动启动

**后端：**

```bash
cd career-ai-agent/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000
```

**前端（新开终端）：**

```bash
cd career-ai-agent/frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## 🎮 使用教程

### 求职者

```
1. 打开 http://localhost:3000
2. 点击「上传简历」选择 PDF
3. 上传后点击快捷按钮或直接输入：
   - 「帮我分析这份简历」→ 获取评估报告
   - 「开始面试」→ 进入模拟面试
   - 「帮我匹配 AI Agent 岗位」→ 人岗匹配
   - 「帮我优化简历」→ 逐条修改建议
```

### HR 招聘官

```
1. 右上角切换角色为「HR 招聘官」
2. 「面试题库」→ 按分类生成面试题
```

### 开发者

```
1. 右上角切换角色为「开发者」
2. 「系统架构」→ 查看技术栈和架构设计
3. 「API 调试」→ 可视化调用接口
4. 「性能监控」→ 查看调用数据
```

---

## 🧠 技术架构

```
用户 → [Next.js 16 前端] → SSE 流式 → [FastAPI 后端]
                                              │
                    LangGraph StateGraph Workflow
                    ┌──────────────────────────────────┐
                    │  Router Agent → 分类用户意图       │
                    │    ├─ Resume Agent  → 简历分析      │
                    │    ├─ Match Agent   → 人岗匹配      │
                    │    ├─ Optimize Agent → 简历优化     │
                    │    ├─ Interview Agent → 模拟面试    │
                    │    └─ Knowledge Agent → 职业咨询    │
                    │         ↓                         │
                    │    Summary Agent → 整合回复        │
                    └──────────────────────────────────┘
                              │
                    ChromaDB 向量库 ← → DeepSeek API
```

### 技术栈

| 前端 | 后端 | AI / 数据 | DevOps |
|------|------|----------|--------|
| Next.js 16 | Python 3.13 | DeepSeek API | Docker |
| TypeScript | FastAPI | ChromaDB | GitHub |
| Tailwind CSS | LangGraph | PyMuPDF | SSE 流式 |

---

## 📂 项目结构

```
career-ai-agent/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── agents/             # 6 个 Agent 定义 + LLM 客户端
│   │   ├── skills/             # Skills 标准化封装
│   │   ├── prompts/            # 分层 Prompt 模板
│   │   ├── rag/                # 混合检索 (BM25 + ChromaDB)
│   │   ├── routers/            # API 路由 (chat/upload/health)
│   │   ├── models/             # 数据模型
│   │   └── services/           # PDF 解析 + 会话管理
│   ├── tests/                  # 83 个单元测试
│   └── .env.example            # 配置模板
├── frontend/                   # Next.js 前端
│   ├── app/                    # 页面
│   ├── components/             # UI 组件
│   └── lib/                    # API 客户端 + 类型
├── docker-compose.yml          # Docker 一键部署
└── README.md                   # 使用手册
```

---

## 📊 测试

项目包含 **83 个测试用例**（全部通过），覆盖核心逻辑：

```bash
cd career-ai-agent/backend
python3 -m pytest tests/ -v
```

---

## ⚠️ 常见问题

| 问题 | 解决 |
|------|------|
| `pip install` 报错 | 确保 Python 3.13+，用 `python3 -m pip install` |
| `npm install` 报错 | 确保 Node.js 22+ |
| 启动后页面空白 | 检查终端是否有报错，确保后端先启动 |
| API Key 无效 | 去 DeepSeek 官网重新生成 Key |
| 端口被占用 | 修改 `backend/.env` 中的 `SERVER_PORT=8001` |

---

## 📄 License

MIT © 2026 RTY798
