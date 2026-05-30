"use client";

import { useState, useRef } from "react";
import { uploadResume } from "../lib/api";
import ChatArea from "./chat-area";

export default function MatchTab() {
  const [resumeText, setResumeText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  return (
    <div style={{ display: "flex", gap: 16, height: "100%" }}>
      <div style={{ width: 280, flexShrink: 0, display: "flex", flexDirection: "column", gap: 12 }}>
        <div className="panel-card">
          <div className="panel-card-title">📄 简历</div>
          <div className="dropzone" style={{ padding: 14, cursor: "pointer", textAlign: "center" }}
            onClick={() => fileRef.current?.click()}>
            <input ref={fileRef} type="file" accept=".pdf" hidden
              onChange={async (e) => { const f = e.target.files?.[0]; if (f) { setResumeFile(f); try { const t = await uploadResume(f); setResumeText(t); } catch {} } }} />
            {resumeFile ? <span style={{ fontWeight: 500, fontSize: 12 }}>📎 {resumeFile.name}</span> : "📄 上传简历"}
          </div>
        </div>
        <div className="panel-card" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <div className="panel-card-title">📋 职位描述</div>
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="粘贴职位描述（JD）..."
            className="input"
            style={{ flex: 1, minHeight: 150, borderRadius: "var(--radius-sm)" }}
          />
        </div>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <ChatArea
          resumeText={resumeText} jdText={jdText}
          initialMessage={resumeText && jdText
            ? "简历和职位描述已就绪！正在等待你的指令...\n\n试试说：**「帮我匹配这个岗位」**"
            : "👋 上传简历并粘贴职位描述，我帮你做匹配分析。"}
        />
      </div>
    </div>
  );
}
