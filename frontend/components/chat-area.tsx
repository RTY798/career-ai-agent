"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import type { ChatMessage } from "../lib/types";
import { sendMessage } from "../lib/api";
import ThoughtChain from "./thought-chain";

interface ChatAreaProps {
  placeholder?: string;
  initialMessage?: string;
  resumeText?: string;
  jdText?: string;
  pendingMessage?: string;
  onResponse?: (reply: string) => void;
  onPendingConsumed?: () => void;
}

// 中文头像：你 / AI
function Avatar({ role }: { role: "user" | "assistant" }) {
  return (
    <div style={{
      width: 28, height: 28, borderRadius: 7, flexShrink: 0, marginTop: 2,
      display: "flex", alignItems: "center", justifyContent: "center",
      background: role === "user"
        ? "linear-gradient(135deg, #2a2a4e, #3a3a6e)"
        : "linear-gradient(135deg, #d4804a25, #e8a07015)",
      color: role === "user" ? "#aabbee" : "#d4804a",
      fontWeight: 600, fontSize: 11,
    }}>
      {role === "user" ? "你" : "AI"}
    </div>
  );
}

export default function ChatArea({
  placeholder = "输入消息... Enter 发送",
  initialMessage,
  resumeText = "",
  jdText = "",
  pendingMessage,
  onResponse,
  onPendingConsumed,
}: ChatAreaProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(
    initialMessage ? [{ role: "assistant" as const, content: initialMessage }] : []
  );
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [convId, setConvId] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scroll = useCallback(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), []);
  useEffect(scroll, [messages]);

  useEffect(() => {
    if (pendingMessage && !loading) {
      setInput(pendingMessage);
      onPendingConsumed?.();
      const msg = pendingMessage;
      setTimeout(() => {
        setInput(""); setLoading(true);
        setMessages((p) => [...p, { role: "user", content: msg }]);
        sendMessage(msg, resumeText, jdText, convId || undefined).then((r) => {
          if (r.conversation_id) setConvId(r.conversation_id);
          setMessages((p) => [...p, { role: "assistant", content: r.reply || "你好！", thoughts: r.thought_chain, report: r.interview_report || undefined }]);
          onResponse?.(r.reply);
        }).catch((e) => setMessages((p) => [...p, { role: "assistant", content: `错误：${e instanceof Error ? e.message : "请求失败"}` }]))
          .finally(() => { setLoading(false); inputRef.current?.focus(); });
      }, 0);
    }
  }, [pendingMessage]);

  const send = async () => {
    const msg = input.trim();
    if (!msg || loading) return;
    setInput(""); setLoading(true);
    setMessages((p) => [...p, { role: "user", content: msg }]);
    try {
      const r = await sendMessage(msg, resumeText, jdText, convId || undefined);
      if (r.conversation_id) setConvId(r.conversation_id);
      setMessages((p) => [...p, { role: "assistant", content: r.reply || "你好！", thoughts: r.thought_chain, report: r.interview_report || undefined }]);
      onResponse?.(r.reply);
    } catch (e) {
      setMessages((p) => [...p, { role: "assistant", content: `错误：${e}` }]);
    } finally { setLoading(false); inputRef.current?.focus(); }
  };

  return (
    <div style={{
      display: "flex", flexDirection: "column", height: "100%",
      background: "#0d0d1a", borderRadius: 16,
      border: "1px solid rgba(255,255,255,0.06)", overflow: "hidden",
      boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
    }}>
      {/* Messages — dark tech bg */}
      <div style={{
        flex: 1, overflowY: "auto",
        background: `
          radial-gradient(ellipse 60% 40% at 20% 80%, rgba(212,128,74,0.03) 0%, transparent 60%),
          radial-gradient(ellipse 50% 30% at 80% 20%, rgba(74,143,212,0.03) 0%, transparent 60%),
          #0d0d1a
        `,
        padding: "20px 16px 12px",
        display: "flex", flexDirection: "column", gap: 16,
      }}>
        {messages.length === 0 && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8, padding: "60px 20px" }}>
            <div style={{ fontSize: 28, opacity: 0.3 }}>💬</div>
            <div style={{ fontSize: 13, color: "rgba(255,255,255,0.25)" }}>开始对话</div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className="anim-fade-up" style={{
            display: "flex", gap: 10,
            flexDirection: msg.role === "user" ? "row-reverse" : "row",
            alignItems: "flex-start",
          }}>
            <Avatar role={msg.role} />
            <div style={{
              maxWidth: "78%", padding: "10px 14px",
              fontSize: 13, lineHeight: 1.65, whiteSpace: "pre-wrap",
              borderRadius: msg.role === "user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
              background: msg.role === "user" ? "rgba(42,42,78,0.6)" : "rgba(255,255,255,0.04)",
              color: msg.role === "user" ? "rgba(255,255,255,0.85)" : "rgba(255,255,255,0.8)",
              backdropFilter: msg.role === "user" ? "none" : "blur(8px)",
            }}>
              {msg.content}
              {msg.thoughts?.length ? (
                <details style={{ marginTop: 8 }}>
                  <summary style={{
                    fontSize: 11, color: "rgba(255,255,255,0.3)",
                    cursor: "pointer",
                  }}>
                    Agent 处理过程 ({msg.thoughts.length} 步)
                  </summary>
                  <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 4 }}>
                    {msg.thoughts.map((t, j) => (
                      <div key={j} style={{
                        fontSize: 11, display: "flex", gap: 6,
                        color: "rgba(255,255,255,0.5)",
                      }}>
                        <span>{t.status === "completed" ? "✓" : t.status === "error" ? "✕" : "○"}</span>
                        <span style={{ fontWeight: 500 }}>{t.agent}</span>
                        {t.output && <span style={{ opacity: 0.6 }}>— {t.output}</span>}
                      </div>
                    ))}
                  </div>
                </details>
              ) : null}
              {msg.report && (
                <div style={{ marginTop: 10, padding: 12, background: "rgba(230,81,0,0.1)", borderRadius: 8, border: "1px solid rgba(230,81,0,0.15)" }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#e8a070", marginBottom: 6 }}>📋 面试报告</div>
                  <div style={{ fontSize: 22, fontWeight: 700, color: "rgba(255,255,255,0.9)", marginBottom: 8 }}>
                    {String(msg.report.overall_score ?? "-")}/100
                  </div>
                  {(() => {
                    const ds = msg.report?.dimension_scores;
                    if (ds && typeof ds === "object") {
                      return Object.entries(ds as Record<string, number>).map(([k, v]) => (
                        <div key={k} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3, fontSize: 11 }}>
                          <span style={{ width: 70, color: "rgba(255,255,255,0.5)" }}>{k}</span>
                          <div style={{ flex: 1, height: 3, background: "rgba(255,255,255,0.08)", borderRadius: 2, overflow: "hidden" }}>
                            <div style={{ height: "100%", width: `${Math.min(v, 100)}%`, background: "linear-gradient(90deg, #d4804a, #e8a070)", borderRadius: 2, transition: "width 0.5s" }} />
                          </div>
                          <span style={{ fontWeight: 600, width: 24, textAlign: "right", color: "rgba(255,255,255,0.6)" }}>{v}</span>
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
          <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
            <Avatar role="assistant" />
            <div style={{ display: "flex", gap: 4, padding: "12px 16px", background: "rgba(255,255,255,0.04)", borderRadius: "14px 14px 14px 4px" }}>
              <span className="typing-dot" style={{ background: "rgba(255,255,255,0.3)" }} />
              <span className="typing-dot" style={{ background: "rgba(255,255,255,0.3)" }} />
              <span className="typing-dot" style={{ background: "rgba(255,255,255,0.3)" }} />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input — dark */}
      <div style={{
        padding: "12px 16px 14px",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        background: "#0d0d1a",
      }}>
        <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder={placeholder}
            rows={1}
            style={{
              flex: 1, outline: "none", resize: "none", fontFamily: "inherit",
              padding: "9px 14px", fontSize: 13, lineHeight: 1.4,
              border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10,
              background: "rgba(255,255,255,0.04)", color: "rgba(255,255,255,0.8)",
              minHeight: 36,
              transition: "border-color 0.15s",
            }}
            onFocus={(e) => e.currentTarget.style.borderColor = "rgba(212,128,74,0.4)"}
            onBlur={(e) => e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"}
          />
          <button onClick={send} disabled={loading || !input.trim()} style={{
            height: 36, padding: "0 16px", border: "none", borderRadius: 10,
            background: loading || !input.trim() ? "rgba(255,255,255,0.06)" : "linear-gradient(135deg, #d4804a, #e8a070)",
            color: "white", fontSize: 13, fontWeight: 600,
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            transition: "all 0.15s", flexShrink: 0,
            opacity: loading || !input.trim() ? 0.3 : 1,
          }}>
            发送
          </button>
        </div>
      </div>
    </div>
  );
}
