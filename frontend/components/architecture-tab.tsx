"use client";

import ChatArea from "./chat-area";

const LAYERS = [
  {
    title: "🎯 前端层",
    items: ["Next.js 16 + React 19", "TypeScript + Tailwind CSS v4", "SSE 流式事件驱动"],
    color: "var(--color-accent)",
  },
  {
    title: "🔌 API 层",
    items: ["FastAPI + Uvicorn", "REST: /api/chat, /api/upload", "SSE: /api/chat/stream"],
    color: "#2E7D32",
  },
  {
    title: "🤖 Agent 层",
    items: ["LangGraph StateGraph", "6 Agent 协作 (Router/Resume/Match/Optimize/Interview/Knowledge)", "Skills 标准化封装 + 版本号"],
    color: "#1565C0",
  },
  {
    title: "🧠 AI 层",
    items: ["DeepSeek API (OpenAI 兼容)", "分层 Prompt 体系", "多模型适配管理器"],
    color: "#6A1B9A",
  },
  {
    title: "📦 数据层",
    items: ["ChromaDB 向量数据库", "BM25 + 语义混合检索", "Session Store 对话记忆"],
    color: "#C47A3A",
  },
  {
    title: "🐳 部署",
    items: ["Docker Compose", "Nginx (可选)", "一键启动脚本"],
    color: "#E65100",
  },
];

export default function ArchitectureTab() {
  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      <div style={{ width: 240, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12, overflow: "hidden" }}>
        <div className="panel-card" style={{ overflow: "hidden" }}>
          <div className="panel-card-title">🏗️ 系统架构</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {LAYERS.map((layer, i) => (
              <div key={layer.title} style={{
                background: "var(--color-bg)", borderRadius: "var(--radius-sm)", padding: 10,
                borderLeft: `3px solid ${layer.color}`,
              }}>
                <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 4 }}>{layer.title}</div>
                {layer.items.map((item) => (
                  <div key={item} style={{ fontSize: 10, color: "var(--color-text-secondary)", lineHeight: 1.6, paddingLeft: 4 }}>
                    • {item}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <ChatArea
          initialMessage="🏗️ **系统架构**\n\n当前系统采用 6 层架构：\n\n**数据流向：**\n`用户 → Next.js → FastAPI → LangGraph Agent → LLM API`\n\n可以问我：\n- 「Agent 工作流是怎么设计的？」\n- 「RAG 混合检索怎么做？」\n- 「SSE 流式怎么实现的？」"
        />
      </div>
    </div>
  );
}
