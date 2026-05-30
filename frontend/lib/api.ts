import type { ChatMessage, ChatResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function sendMessage(
  message: string,
  resume?: string,
  jd?: string,
  conversationId?: string,
  onThought?: (thought: Record<string, unknown>) => void,
): Promise<ChatResponse> {
  // SSE streaming
  if (onThought) {
    return streamChat(message, resume, jd, conversationId, onThought);
  }

  // Fallback to sync
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      resume: resume || undefined,
      jd: jd || undefined,
      conversation_id: conversationId || undefined,
    }),
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function streamChat(
  message: string,
  resume?: string,
  jd?: string,
  conversationId?: string,
  onThought?: (thought: Record<string, unknown>) => void,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      resume: resume || undefined,
      jd: jd || undefined,
      conversation_id: conversationId || undefined,
    }),
  });

  if (!response.ok) throw new Error(`Stream error: ${response.status}`);
  if (!response.body) throw new Error("No response body");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const result: ChatResponse = {
    reply: "",
    intent: "",
    thought_chain: [],
  };

  return new Promise((resolve, reject) => {
    function processChunk(): void {
      reader
        .read()
        .then(({ done, value }) => {
          if (done) {
            resolve(result);
            return;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              const eventType = line.slice(7).trim();
              // next line should be data:
              continue;
            }
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.agent) {
                  result.thought_chain.push(data);
                  if (onThought) onThought(data);
                } else if (data.content) {
                  result.reply = data.content;
                } else if (data.overall_score) {
                  result.interview_report = data;
                }
              } catch { /* ignore */ }
            }
          }

          processChunk();
        })
        .catch(reject);
    }

    processChunk();
  });
}

/** 上传 PDF 简历，提取文本 */
export async function uploadResume(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("上传失败");
  const data = await res.json();
  return data.text;
}
