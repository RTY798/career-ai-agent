"use client";

import { useState, useCallback } from "react";
import ChatArea from "./chat-area";

const QUICK_TOPICS = [
  { icon: "🤖", label: "Agent 技能", msg: "AI Agent 开发需要学习哪些技能？" },
  { icon: "📊", label: "就业形势", msg: "2026年 AI 方向的就业形势怎么样？" },
  { icon: "📝", label: "简历技巧", msg: "技术简历怎么写才更容易通过筛选？" },
  { icon: "🎤", label: "面试准备", msg: "AI Agent 岗位面试一般问什么？" },
  { icon: "📚", label: "学习路径", msg: "零基础怎么入行 AI Agent 开发？" },
  { icon: "💰", label: "薪资参考", msg: "AI Agent 开发工程师的薪资范围？" },
];

export default function AdviceTab() {
  const [sendMsg, setSendMsg] = useState("");
  const onQuick = useCallback((msg: string) => setSendMsg(msg), []);
  const onConsumed = useCallback(() => setSendMsg(""), []);

  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      <div style={{ width: 200, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card">
          <div className="panel-card-title">💡 热门问题</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {QUICK_TOPICS.map((q) => (
              <button key={q.label} className="btn btn-ghost" style={{ justifyContent: "flex-start", fontSize: 12, padding: "8px 10px", borderRadius: "var(--radius-sm)" }}
                onClick={() => onQuick(q.msg)}>
                {q.icon} {q.label}
              </button>
            ))}
          </div>
        </div>
        <div className="panel-card">
          <div className="panel-card-title">📚 知识库</div>
          <div style={{ fontSize: 11, color: "var(--color-text-muted)", lineHeight: 1.7 }}>
            内置求职 FAQ、面试技巧、行业分析，回答基于知识库检索。
          </div>
        </div>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <ChatArea
          pendingMessage={sendMsg}
          onPendingConsumed={onConsumed}
          initialMessage="👋 你好！我是 CareerAI\n\n关于求职、职业发展、技能学习等问题都可以问我。\n\n💡 点左侧热门问题快速开始，或直接打字提问。"
        />
      </div>
    </div>
  );
}
