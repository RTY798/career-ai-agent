"use client";

import { useState, useRef, useEffect } from "react";
import { sendMessage, uploadResume } from "../lib/api";
import type { ChatMessage } from "../lib/types";
import ThoughtChain from "./thought-chain";

export default function InterviewTab() {
  const [messages, setMessages] = useState<ChatMessage[]>([{
    role: "assistant", content: "🎤 **模拟面试**\n\n准备好后点击「开始面试」，我会根据你的情况进行多轮面试。每轮我会出题、评分，最后生成完整报告。",
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [convId, setConvId] = useState<string | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [started, setStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = async (msg: string) => {
    if (!msg.trim() || loading) return;
    setInput(""); setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    try {
      const r = await sendMessage(msg, resumeText, "", convId || undefined);
      if (r.conversation_id) setConvId(r.conversation_id);
      setMessages((prev) => [...prev, { role: "assistant", content: r.reply || "面试已结束", thoughts: r.thought_chain, report: r.interview_report || undefined }]);
      if (!started) setStarted(true);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: `❌ 错误：${e}` }]);
    } finally { setLoading(false); }
  };

  const startInterview = () => send("开始面试");
  const endInterview = () => send("结束面试");

  const qCount = messages.filter((m) => m.role === "assistant" && m.content.includes("第")).length;

  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      {/* Sidebar */}
      <div style={{ width: 200, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card">
          <div className="panel-card-title">🎤 面试</div>
          <div style={{ fontSize: 12, color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
            <div className="dropzone" style={{ padding: 12, cursor: "pointer", marginBottom: 8, textAlign: "center" }}
              onClick={() => fileRef.current?.click()}>
              <input ref={fileRef} type="file" accept=".pdf" hidden
                onChange={async (e) => { const f = e.target.files?.[0]; if (f) { setResumeFile(f); try { const t = await uploadResume(f); setResumeText(t); } catch {} } }} />
              {resumeFile ? <span style={{ fontWeight: 500 }}>📎 {resumeFile.name}</span> : "📄 上传简历作为面试基础"}
            </div>
          </div>
        </div>

        {started && (
          <div className="panel-card">
            <div className="panel-card-title">📊 进度</div>
            <div className="progress-bar" style={{ marginBottom: 6 }}>
              <div className="progress-fill" style={{ width: `${Math.min(qCount * 20, 100)}%` }} />
            </div>
            <div className="text-muted" style={{ fontSize: 11, display: "flex", justifyContent: "space-between" }}>
              <span>已答 {qCount} 题</span>
            </div>
          </div>
        )}

        {!started ? (
          <button className="btn btn-primary btn-block" onClick={startInterview} disabled={loading} style={{ fontSize: 13, padding: "11px 0" }}>
            开始面试
          </button>
        ) : (
          <button className="btn btn-outline btn-block" onClick={endInterview} disabled={loading} style={{ fontSize: 12, padding: "9px 0" }}>
            结束面试
          </button>
        )}
      </div>

      {/* Chat */}
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <div className="panel-card" style={{ flex: 1, display: "flex", flexDirection: "column", padding: 0, overflow: "hidden" }}>
          <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
            {messages.map((msg, i) => (
              <div key={i} className="anim-fade-up" style={{ display: "flex", gap: 8, flexDirection: msg.role === "user" ? "row-reverse" : "row", alignItems: "flex-start" }}>
                <div style={{ width: 28, height: 28, borderRadius: "50%", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, background: msg.role === "user" ? "var(--color-primary)" : "var(--color-accent-soft)" }}>
                  {msg.role === "user" ? "👤" : "🎤"}
                </div>
                <div className={`chat-bubble ${msg.role}`}>
                  <div style={{ lineHeight: 1.65 }}>{msg.content}</div>
                  {msg.thoughts?.length ? <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--color-border-light)" }}><ThoughtChain thoughts={msg.thoughts} /></div> : null}
                  {msg.report && (
                    <div style={{ marginTop: 10, padding: 12, background: "var(--color-warning-bg)", borderRadius: "var(--radius-sm)" }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: "var(--color-warning)", marginBottom: 6 }}>📋 面试报告</div>
                      <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>总分：{String(msg.report.overall_score ?? "-")}/100</div>
                      {(() => {
                        const ds = msg.report?.dimension_scores;
                        if (ds && typeof ds === "object") {
                          return Object.entries(ds as Record<string, number>).map(([k, v]) => (
                            <div key={k} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4, fontSize: 12 }}>
                              <span style={{ width: 80, color: "var(--color-text-secondary)" }}>{k}</span>
                              <div className="progress-bar" style={{ flex: 1, height: 4 }}><div className="progress-fill" style={{ width: `${Math.min(v, 100)}%` }} /></div>
                              <span style={{ fontWeight: 600, width: 30, textAlign: "right" }}>{v}</span>
                            </div>
                          ));
                        }
                        return null;
                      })()}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <div style={{ width: 28, height: 28, borderRadius: "50%", background: "var(--color-accent-soft)", display: "flex", alignItems: "center", justifyContent: "center" }}>🎤</div>
                <div style={{ display: "flex", gap: 4, padding: "10px 16px", background: "var(--color-surface)", border: "1px solid var(--color-border-light)", borderRadius: 16 }}>
                  <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
                  <span style={{ fontSize: 11, color: "var(--color-text-muted)", marginLeft: 4 }}>AI 思考中...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div style={{ padding: "12px 16px", borderTop: "1px solid var(--color-border-light)", display: "flex", gap: 8 }}>
            <textarea
              value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); if (started) send(input); } }}
              placeholder={started ? "输入你的回答..." : "点击「开始面试」按钮启动"}
              rows={1} disabled={!started}
              className="input"
              style={{ flex: 1, borderRadius: "var(--radius-md)", fontSize: 13, padding: "10px 14px" }}
            />
            <button className="btn btn-primary" onClick={() => send(input)} disabled={loading || !input.trim() || !started}
              style={{ alignSelf: "flex-end", padding: "10px 18px", borderRadius: "var(--radius-md)" }}>
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
