"use client";

import { useState } from "react";

const ENDPOINTS = [
  { label: "健康检查", endpoint: "/api/health", method: "GET", body: "" },
  { label: "聊天", endpoint: "/api/chat", method: "POST", body: '{"message": "hello"}' },
  { label: "流式聊天", endpoint: "/api/chat/stream", method: "POST", body: '{"message": "hello"}' },
];

export default function ApiTab() {
  const [selected, setSelected] = useState(ENDPOINTS[0]);
  const [body, setBody] = useState(selected.body);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const callApi = async () => {
    setLoading(true); setResponse("");
    try {
      const opts: RequestInit = { method: selected.method };
      if (selected.method === "POST") {
        opts.headers = { "Content-Type": "application/json" };
        opts.body = body;
      }
      const start = performance.now();
      const resp = await fetch(`http://127.0.0.1:8000${selected.endpoint}`, opts);
      const elapsed = (performance.now() - start).toFixed(0);
      const text = await resp.text();
      setResponse(`Status: ${resp.status} (${elapsed}ms)\n\n${text.substring(0, 2000)}`);
    } catch (e) {
      setResponse(`Error: ${e}`);
    } finally { setLoading(false); }
  };

  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      <div style={{ width: 200, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card">
          <div className="panel-card-title">🔌 API 端点</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {ENDPOINTS.map((ep) => (
              <button key={ep.label} className={`btn btn-ghost ${selected.label === ep.label ? "active" : ""}`}
                style={{ justifyContent: "flex-start", fontSize: 12, padding: "8px 10px", borderRadius: "var(--radius-sm)",
                  ...(selected.label === ep.label ? { background: "var(--color-accent-soft)", color: "var(--color-accent)", fontWeight: 600 } : {}) }}
                onClick={() => { setSelected(ep); setBody(ep.body); setResponse(""); }}>
                <span className={`badge ${ep.method === "GET" ? "badge-green" : "badge-accent"}`} style={{ fontSize: 9, padding: "1px 6px" }}>{ep.method}</span>
                {ep.label}
              </button>
            ))}
          </div>
        </div>
        <button className="btn btn-primary btn-block" onClick={callApi} disabled={loading}
          style={{ fontSize: 12, padding: "10px 0" }}>
          {loading ? "请求中..." : "发送请求"}
        </button>
      </div>
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <div className="panel-card-title">📤 请求</div>
          <div style={{ fontSize: 11, color: "var(--color-text-muted)", marginBottom: 6 }}>
            <span className="badge badge-accent" style={{ fontSize: 10 }}>{selected.method}</span>
            <code style={{ marginLeft: 6, fontSize: 12 }}>{selected.endpoint}</code>
          </div>
          {selected.method === "POST" && (
            <textarea className="input" value={body} onChange={(e) => setBody(e.target.value)}
              style={{ flex: 1, minHeight: 100, fontFamily: "monospace", fontSize: 12, borderRadius: "var(--radius-sm)" }} />
          )}
        </div>
        <div className="panel-card" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <div className="panel-card-title">📥 响应</div>
          <textarea className="input" value={response} readOnly
            style={{ flex: 1, minHeight: 150, fontFamily: "monospace", fontSize: 12, borderRadius: "var(--radius-sm)", background: "var(--color-bg)" }}
            placeholder="点击「发送请求」查看响应..." />
        </div>
      </div>
    </div>
  );
}
