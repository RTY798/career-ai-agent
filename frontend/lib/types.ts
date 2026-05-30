export type Role = "job_seeker" | "hr" | "developer";

export type TabId =
  | "resume"
  | "interview"
  | "match"
  | "optimize"
  | "advice"
  | "questions"
  | "architecture"
  | "api"
  | "monitor";

export interface TabDef {
  id: TabId;
  label: string;
  icon: string;
}

export const ROLE_TABS: Record<Role, TabDef[]> = {
  job_seeker: [
    { id: "resume", label: "简历分析", icon: "📄" },
    { id: "interview", label: "模拟面试", icon: "🎤" },
    { id: "match", label: "人岗匹配", icon: "🎯" },
    { id: "optimize", label: "简历优化", icon: "✏️" },
    { id: "advice", label: "职业咨询", icon: "💡" },
  ],
  hr: [
    { id: "questions", label: "面试题库", icon: "📚" },
  ],
  developer: [
    { id: "architecture", label: "系统架构", icon: "🏗️" },
    { id: "api", label: "API 调试", icon: "🔌" },
    { id: "monitor", label: "性能监控", icon: "📊" },
  ],
};

export const ROLE_LABELS: Record<Role, string> = {
  job_seeker: "🎯 求职者",
  hr: "👔 HR 招聘官",
  developer: "🧑‍💻 开发者",
};

export interface AgentThought {
  agent: string;
  status: "running" | "completed" | "error";
  input?: string;
  output?: string;
  error?: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  thoughts?: AgentThought[];
  report?: Record<string, unknown>;
}

export interface ChatResponse {
  reply: string;
  intent: string;
  thought_chain: AgentThought[];
  parsed_resume?: Record<string, unknown>;
  match_result?: Record<string, unknown>;
  optimize_report?: Record<string, unknown>;
  interview_report?: Record<string, unknown>;
  conversation_id?: string;
}

export interface UploadState {
  resume: File | null;
  jdText: string;
}
