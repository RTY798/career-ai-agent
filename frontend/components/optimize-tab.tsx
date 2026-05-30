"use client";

import { useState, useRef } from "react";
import { uploadResume } from "../lib/api";
import ChatArea from "./chat-area";

export default function OptimizeTab() {
  const [resumeText, setResumeText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      <div style={{ width: 220, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card">
          <div className="panel-card-title">✏️ 简历优化</div>
          <div className="dropzone" style={{ padding: resumeFile ? 16 : 24, cursor: "pointer", textAlign: "center" }}
            onClick={() => fileRef.current?.click()}>
            <input ref={fileRef} type="file" accept=".pdf" hidden
              onChange={async (e) => { const f = e.target.files?.[0]; if (f) { setResumeFile(f); try { const t = await uploadResume(f); setResumeText(t); } catch {} } }} />
            {resumeFile ? (
              <div><div style={{ fontSize: 28 }}>📎</div><div style={{ fontSize: 12, fontWeight: 600, marginTop: 4 }}>{resumeFile.name}</div></div>
            ) : (
              <div><div style={{ fontSize: 32 }}>📄</div><div style={{ fontSize: 12, marginTop: 4 }}>上传简历</div></div>
            )}
          </div>
        </div>
        {resumeText && (
          <div className="panel-card">
            <div className="panel-card-title">🔍 检测维度</div>
            <div style={{ fontSize: 12, color: "var(--color-text-secondary)", lineHeight: 1.8 }}>
              {["空洞动词 → 具体行动", "补充量化数据", "增强措辞力度", "补充缺失技能", "统一格式规范"].map((s) => (
                <div key={s} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ color: "var(--color-success)" }}>✓</span> {s}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <ChatArea
          resumeText={resumeText}
          initialMessage={resumeText
            ? "简历已上传！试试：\n\n• 「帮我全面优化」\n• 「针对 AI Agent 岗位优化」\n• 「优化项目描述部分」"
            : "上传简历后，我会分析并给出逐条优化建议。"}
        />
      </div>
    </div>
  );
}
