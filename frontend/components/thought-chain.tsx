"use client";
import type { AgentThought } from "../lib/types";

export default function ThoughtChain({ thoughts }: { thoughts: AgentThought[] }) {
  if (!thoughts?.length) return null;
  return (
    <details>
      <summary style={{ fontSize: 12, color: "var(--color-text-muted)", cursor: "pointer", userSelect: "none" }}>
        🤔 Agent 处理过程 ({thoughts.length} 步)
      </summary>
      <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
        {thoughts.map((t, i) => (
          <ThoughtStep key={i} thought={t} />
        ))}
      </div>
    </details>
  );
}

function ThoughtStep({ thought }: { thought: AgentThought }) {
  const label = thought.status === "completed" ? "✅" : thought.status === "error" ? "❌" : "⏳";
  return (
    <div style={{ fontSize: 12, color: "var(--color-text-secondary)", display: "flex", gap: 6, alignItems: "flex-start" }}>
      <span>{label}</span>
      <div>
        <span style={{ fontWeight: 600 }}>{thought.agent}</span>
        {thought.output && <span style={{ color: "var(--color-text-muted)" }}> — {thought.output}</span>}
        {thought.error && <span style={{ color: "var(--color-error)" }}> — {thought.error}</span>}
      </div>
    </div>
  );
}
