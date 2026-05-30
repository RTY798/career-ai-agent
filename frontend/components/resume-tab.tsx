"use client";

import { useState, useRef, useCallback } from "react";
import { uploadResume } from "../lib/api";
import ChatArea from "./chat-area";

export default function ResumeTab() {
  const [resumeText, setResumeText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [sendMsg, setSendMsg] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) { setError("请上传 PDF 文件"); return; }
    setUploading(true); setError("");
    try { const text = await uploadResume(file); setResumeText(text); setResumeFile(file); }
    catch { setError("上传失败，请确认 PDF 文件有效"); }
    finally { setUploading(false); }
  };

  const onQuickAction = useCallback((msg: string) => setSendMsg(msg), []);
  const onPendingConsumed = useCallback(() => setSendMsg(""), []);

  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      <div style={{ width: 220, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card">
          <div className="panel-card-title">📄 简历</div>
          <div className="dropzone" style={{ cursor: "pointer", padding: resumeFile ? 16 : 24 }}
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) handleUpload(f); }}>
            <input ref={fileRef} type="file" accept=".pdf" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f); }} />
            {resumeFile ? (
              <div>
                <div style={{ fontSize: 28 }}>📎</div>
                <div style={{ fontSize: 12, fontWeight: 600, marginTop: 6, color: "var(--color-text)" }}>{resumeFile.name}</div>
                <div className="badge badge-green" style={{ marginTop: 6 }}>已识别 · {(resumeText.length / 1000).toFixed(1)}K 字</div>
              </div>
            ) : uploading ? (
              <div><div style={{ fontSize: 28 }}>⏳</div><div style={{ fontSize: 12, marginTop: 6 }}>解析中...</div></div>
            ) : (
              <div>
                <div style={{ fontSize: 36, marginBottom: 4 }}>📄</div>
                <div style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)" }}>上传简历 PDF</div>
                <div className="text-muted" style={{ fontSize: 11, marginTop: 4 }}>拖拽或点击上传</div>
              </div>
            )}
          </div>
          {error && <div style={{ fontSize: 11, color: "var(--color-error)", marginTop: 6, padding: "4px 8px", background: "var(--color-error-bg)", borderRadius: 6 }}>{error}</div>}
        </div>

        {resumeText && (
          <div className="panel-card">
            <div className="panel-card-title">⚡ 快捷操作</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {[
                { label: "📊 分析简历", msg: "帮我全面分析这份简历的优缺点" },
                { label: "🎯 匹配岗位", msg: "帮我匹配 AI Agent 开发工程师岗位" },
                { label: "✏️ 优化简历", msg: "帮我优化这份简历" },
                { label: "🎤 模拟面试", msg: "开始面试" },
              ].map((s) => (
                <button key={s.label} className="btn btn-ghost" style={{ justifyContent: "flex-start", fontSize: 12, padding: "8px 12px", borderRadius: "var(--radius-sm)" }}
                  onClick={() => onQuickAction(s.msg)}>
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <ChatArea
          resumeText={resumeText}
          pendingMessage={sendMsg}
          onPendingConsumed={onPendingConsumed}
          initialMessage={resumeFile
            ? `✅ 已识别简历 **${resumeFile.name}**\n\n你可以：\n• 📊 分析简历 — 获取完整评估报告\n• 🎯 匹配岗位 — 对比职位要求\n• ✏️ 优化简历 — 逐条修改建议\n• 🎤 模拟面试 — 多轮面试练习`
            : "👋 你好！我是 CareerAI\n\n请上传你的简历 PDF，我来帮你分析、匹配岗位或模拟面试。"}
        />
      </div>
    </div>
  );
}
