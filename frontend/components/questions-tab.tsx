"use client";

import { useState, useCallback } from "react";
import ChatArea from "./chat-area";

const CATEGORIES = [
  { id: "technical", label: "💻 技术题", msg: "模拟面试，考察 LangGraph 和 Agent 开发技术" },
  { id: "behavioral", label: "👤 行为题", msg: "模拟面试，考察团队协作和项目管理经验" },
  { id: "project", label: "📁 项目深挖", msg: "模拟面试，深挖项目经验和架构决策" },
  { id: "system", label: "🏗️ 系统设计", msg: "模拟面试，考察系统设计能力" },
  { id: "mixed", label: "📋 综合套题", msg: "开始面试，包含技术、行为、项目的完整面试" },
];

export default function QuestionsTab() {
  const [sendMsg, setSendMsg] = useState("");
  const onQuick = useCallback((msg: string) => setSendMsg(msg), []);
  const onConsumed = useCallback(() => setSendMsg(""), []);

  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      <div style={{ width: 200, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card">
          <div className="panel-card-title">📚 题库分类</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {CATEGORIES.map((c) => (
              <button key={c.id} className="btn btn-ghost" style={{ justifyContent: "flex-start", fontSize: 12, padding: "8px 10px", borderRadius: "var(--radius-sm)" }}
                onClick={() => onQuick(c.msg)}>
                {c.label}
              </button>
            ))}
          </div>
        </div>
        <div className="panel-card">
          <div className="panel-card-title">💡 用法</div>
          <div style={{ fontSize: 11, color: "var(--color-text-muted)", lineHeight: 1.7 }}>
            点分类自动开始模拟面试，或直接描述你想要什么类型的面试题。
          </div>
        </div>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <ChatArea
          pendingMessage={sendMsg}
          onPendingConsumed={onConsumed}
          initialMessage="📚 **面试题库**\n\n点左侧分类快速进入模拟面试，系统会根据你的选择生成对应类型的问题。\n\n或者直接说：\n- **「开始面试」** — 综合面试\n- **「模拟面试，考 LangGraph」** — 技术专项"
        />
      </div>
    </div>
  );
}
