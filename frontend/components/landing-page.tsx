"use client";

import { useState, useEffect, useRef } from "react";

const FEATURES = [
  { icon: "🧠", title: "多 Agent 大脑", desc: "6 个专职 Agent · LangGraph StateGraph 编排", color: "#d4804a" },
  { icon: "📊", title: "简历引擎", desc: "PyMuPDF 解析 · 分层 Prompt · 一致性 90%+", color: "#4a8fd4" },
  { icon: "🎤", title: "面试官", desc: "多轮对话 · 自动评分 · 报告生成", color: "#4ad47a" },
  { icon: "🔍", title: "混合检索 RAG", desc: "BM25 + 向量 · 召回率 78% · 准确率 92%", color: "#d44a8a" },
  { icon: "⚡", title: "SSE 流式", desc: "逐节点推送 · 实时思考链可视化", color: "#d4a04a" },
  { icon: "🔌", title: "多模型适配", desc: "DeepSeek / 通义千问 · 自动降级 · 并发控制", color: "#8a4ad4" },
];

const STATS = [
  { value: "6", label: "Agent 协作", sub: "专职分工" },
  { value: "83", label: "测试通过", sub: "P0+P1 全覆盖" },
  { value: "78%", label: "检索召回率", sub: "BM25 + 向量混合" },
  { value: "1.2K", label: "代码行数", sub: "Python + TypeScript" },
];

const ARCH_LAYERS = [
  { label: "Next.js 16", role: "前端", color: "#4a8fd4" },
  { label: "FastAPI", role: "API", color: "#4ad47a" },
  { label: "LangGraph", role: "Agent", color: "#d4804a" },
  { label: "DeepSeek", role: "LLM", color: "#d44a8a" },
  { label: "ChromaDB", role: "向量库", color: "#d4a04a" },
  { label: "Docker", role: "部署", color: "#8a4ad4" },
];

function useMouseGlow() {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: 0.5, y: 0.5 });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const handler = (e: MouseEvent) => {
      const r = el.getBoundingClientRect();
      setPos({ x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height });
    };
    el.addEventListener("mousemove", handler);
    return () => el.removeEventListener("mousemove", handler);
  }, []);

  return [ref, pos] as const;
}

// Deterministic pseudo-random to avoid SSR hydration mismatch
function pseudoRandom(seed: number): number {
  const x = Math.sin(seed * 9301 + 49297) * 233280;
  return x - Math.floor(x);
}

// Particle grid — 使用固定值避免水合问题
const PARTICLE_POSITIONS = Array.from({ length: 15 }).map((_, i) => {
  const s = pseudoRandom(i * 7 + 1);
  const s2 = pseudoRandom(i * 13 + 3);
  const s3 = pseudoRandom(i * 17 + 5);
  const s4 = pseudoRandom(i * 23 + 7);
  const s5 = pseudoRandom(i * 29 + 9);
  const s6 = pseudoRandom(i * 31 + 11);
  return {
    x: +(s4 * 100).toFixed(2),
    y: +(s5 * 100).toFixed(2),
    size: +(s * 3 + 1.5).toFixed(2),
    duration: +(8 + s2 * 12).toFixed(2),
    delay: +(s3 * 6).toFixed(2),
    drift: +(s6 * 30 - 15).toFixed(2),
    opacity: +(0.03 + pseudoRandom(i * 37 + 13) * 0.05).toFixed(4),
  };
});

function Particle({ index }: { index: number }) {
  const p = PARTICLE_POSITIONS[index];
  return (
    <div style={{
      position: "absolute", left: `${p.x}%`, top: `${p.y}%`,
      width: p.size, height: p.size, borderRadius: "50%",
      background: `rgba(255,255,255,${p.opacity})`,
      animation: `particleFloat${index % 3} ${p.duration}s infinite`,
      animationDelay: `${p.delay}s`,
      transform: `translateX(${p.drift}px)`,
    }} />
  );
}

export default function LandingPage({ onEnter }: { onEnter: () => void }) {
  const [loaded, setLoaded] = useState(false);
  const [heroRef, heroPos] = useMouseGlow();

  useEffect(() => { setLoaded(true); }, []);

  return (
    <div style={{
      minHeight: "100vh", background: "#08080f",
      fontFamily: '"Inter", "Segoe UI", "PingFang SC", sans-serif',
      position: "relative", overflow: "hidden",
      display: "flex", flexDirection: "column",
    }}>
      {/* ── Animated gradient mesh ── */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 0, overflow: "hidden",
        background: `
          radial-gradient(ellipse 60% 50% at 20% 80%, rgba(212,128,74,0.06) 0%, transparent 60%),
          radial-gradient(ellipse 50% 40% at 80% 20%, rgba(74,143,212,0.06) 0%, transparent 60%),
          radial-gradient(ellipse 40% 50% at 50% 50%, rgba(212,74,138,0.04) 0%, transparent 50%)
        `,
      }}>
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: `linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
        }} />
        {Array.from({ length: 15 }).map((_, i) => <Particle key={i} index={i} />)}
      </div>

      {/* ── Nav ── */}
      <nav style={{
        position: "relative", zIndex: 10,
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "14px 28px",
        background: "rgba(8,8,15,0.6)", backdropFilter: "blur(20px) saturate(180%)",
        borderBottom: "1px solid rgba(255,255,255,0.04)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg, #d4804a, #e8a070)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16, color: "white",
            boxShadow: "0 4px 16px rgba(212,128,74,0.25)",
          }}>🎯</div>
          <span style={{ fontWeight: 700, fontSize: 15, color: "rgba(255,255,255,0.9)", letterSpacing: "-0.2px" }}>CareerAI</span>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <a href="https://github.com/RTY798/career-ai-agent" target="_blank" rel="noopener noreferrer" style={{
              fontSize: 12, color: "rgba(255,255,255,0.3)", cursor: "pointer",
              transition: "color 0.15s", letterSpacing: "0.2px", textDecoration: "none",
            }}
              onMouseEnter={(e) => e.currentTarget.style.color = "rgba(255,255,255,0.6)"}
              onMouseLeave={(e) => e.currentTarget.style.color = ""}>
              GitHub
            </a>
            <span style={{
              fontSize: 12, color: "rgba(255,255,255,0.3)", cursor: "pointer",
              transition: "color 0.15s", letterSpacing: "0.2px",
            }}
              onMouseEnter={(e) => e.currentTarget.style.color = "rgba(255,255,255,0.6)"}
              onMouseLeave={(e) => e.currentTarget.style.color = ""}
              onClick={() => window.open("https://platform.deepseek.com/api_keys", "_blank")}>
              API Key
            </span>
          <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#4ad47a", boxShadow: "0 0 8px rgba(74,212,122,0.5)" }} />
        </div>
      </nav>

      {/* ── Hero ── */}
      <div ref={heroRef} style={{
        flex: 1, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "20px 24px", position: "relative", zIndex: 5,
        opacity: loaded ? 1 : 0, transform: loaded ? "translateY(0)" : "translateY(30px)",
        transition: "all 0.8s cubic-bezier(0.16, 1, 0.3, 1)",
      }}>
        {/* Mouse-follow glow */}
        <div style={{
          position: "absolute", width: 400, height: 400, borderRadius: "50%",
          background: "radial-gradient(circle, rgba(212,128,74,0.06), transparent 70%)",
          left: `${heroPos.x * 100}%`, top: `${heroPos.y * 100}%`,
          transform: "translate(-50%, -50%)",
          transition: "left 0.3s ease-out, top 0.3s ease-out",
          pointerEvents: "none",
        }} />

        {/* Badge */}
        <div className="anim-fade-up" style={{
          padding: "5px 14px", borderRadius: 100,
          background: "rgba(212,128,74,0.1)", border: "1px solid rgba(212,128,74,0.2)",
          fontSize: 10, color: "rgba(255,255,255,0.6)", marginBottom: 28,
          letterSpacing: "0.8px", textTransform: "uppercase",
        }}>
          ✦ 基于 LangGraph · 开源 · MIT
        </div>

        {/* Title with word-level gradient */}
        <h1 style={{
          fontSize: "clamp(32px, 5.5vw, 60px)", fontWeight: 800,
          textAlign: "center", lineHeight: 1.08, marginBottom: 16,
          maxWidth: 700, letterSpacing: "-1.5px",
        }}>
          <span style={{ color: "rgba(255,255,255,0.9)" }}>AI 求职</span>{" "}
          <span style={{
            background: "linear-gradient(135deg, #d4804a 0%, #e8a070 40%, #f0c090 70%, #e8a070 100%)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            backgroundSize: "200% 200%", animation: "gradientShift 4s ease infinite",
          }}>Agent 系统</span>
        </h1>

        <p style={{
          fontSize: "clamp(13px, 1.6vw, 16px)", color: "rgba(255,255,255,0.35)",
          textAlign: "center", maxWidth: 500, lineHeight: 1.7, marginBottom: 32,
        }}>
          基于 LangGraph StateGraph 构建的多 Agent 协作平台。
          简历分析 · 人岗匹配 · 模拟面试 · 职业咨询 — 全流程 AI 驱动。
        </p>

        {/* CTA + secondary */}
        <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 48 }}>
          <button onClick={onEnter} style={{
            padding: "13px 36px", borderRadius: 100, border: "none",
            background: "linear-gradient(135deg, #d4804a, #e8a070)",
            color: "white", fontSize: 14, fontWeight: 700, cursor: "pointer",
            boxShadow: "0 8px 32px rgba(212,128,74,0.25)",
            transition: "all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)",
            letterSpacing: "0.3px", display: "flex", alignItems: "center", gap: 8,
          }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = "scale(1.04) translateY(-2px)"; e.currentTarget.style.boxShadow = "0 12px 40px rgba(212,128,74,0.35)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; }}>
            进入系统 →
          </button>
          <div style={{
            padding: "13px 24px", borderRadius: 100,
            background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)",
            fontSize: 12, color: "rgba(255,255,255,0.3)",
          }}>
            v1.0 · 83 tests passing
          </div>
        </div>

        {/* Tech stack */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center", marginBottom: 40 }}>
          {ARCH_LAYERS.map((t) => (
            <div key={t.label} style={{
              padding: "4px 12px", borderRadius: 6,
              background: `${t.color}12`, border: `1px solid ${t.color}20`,
              fontSize: 11, color: t.color, fontWeight: 500, letterSpacing: "0.2px",
            }}>
              {t.label}
              <span style={{ opacity: 0.4, marginLeft: 4 }}>{t.role}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Stats Bar ── */}
      <div style={{
        position: "relative", zIndex: 5,
        display: "flex", justifyContent: "center", gap: 48,
        padding: "28px 24px",
        background: "rgba(255,255,255,0.02)",
        borderTop: "1px solid rgba(255,255,255,0.04)",
        borderBottom: "1px solid rgba(255,255,255,0.04)",
        flexWrap: "wrap",
      }}>
        {STATS.map((s, i) => (
          <div key={s.label} style={{
            textAlign: "center",
            animation: `fadeUp 0.4s ease-out ${0.2 + i * 0.1}s both`,
          }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: "rgba(255,255,255,0.85)", marginBottom: 1, letterSpacing: "-0.5px" }}>{s.value}</div>
            <div style={{ fontSize: 11, fontWeight: 500, color: "rgba(255,255,255,0.5)" }}>{s.label}</div>
            <div style={{ fontSize: 9, color: "rgba(255,255,255,0.2)", marginTop: 1 }}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* ── 项目简介 ── */}
      <div style={{
        position: "relative", zIndex: 5,
        maxWidth: 700, margin: "0 auto", padding: "40px 24px 0",
        textAlign: "center",
      }}>
        <div style={{
          display: "inline-block", padding: "3px 12px", borderRadius: 100,
          background: "rgba(212,128,74,0.1)", border: "1px solid rgba(212,128,74,0.15)",
          fontSize: 10, color: "rgba(255,255,255,0.5)", marginBottom: 16,
          letterSpacing: "1px",
        }}>
          它能做什么
        </div>
        <h2 style={{
          fontSize: "clamp(20px, 3vw, 28px)", fontWeight: 700,
          color: "rgba(255,255,255,0.85)", marginBottom: 16,
          letterSpacing: "-0.5px",
        }}>
          让 AI 帮你搞定求职全流程
        </h2>

        {/* 三种用户 */}
        <div style={{
          display: "flex", gap: 10, marginBottom: 20,
          flexDirection: "row", justifyContent: "center",
          flexWrap: "wrap",
        }}>
          {[
            {
              icon: "🎓", title: "求职者",
              desc: "上传简历 → 分析匹配度 → 优化简历内容 → 模拟面试练习 → 拿到 offer",
            },
            {
              icon: "👔", title: "HR 招聘官",
              desc: "上传候选人简历 → 四维评估 → 生成面试题 → 快速筛选人才",
            },
            {
              icon: "🧑‍💻", title: "开发者",
              desc: "查看系统架构 → 调试 API 接口 → 监控性能 → 二次开发",
            },
          ].map((u) => (
            <div key={u.title} style={{
              flex: "1 1 180px", maxWidth: 220,
              padding: "14px 14px", borderRadius: 12,
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)",
              textAlign: "left",
            }}>
              <div style={{ fontSize: 20, marginBottom: 6 }}>{u.icon}</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.8)", marginBottom: 4 }}>{u.title}</div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", lineHeight: 1.6 }}>{u.desc}</div>
            </div>
          ))}
        </div>

        {/* 功能介绍 */}
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: 6, marginTop: 4,
        }}>
          {[
            { icon: "📄", label: "简历分析", desc: "上传 PDF 自动解析，多维评分" },
            { icon: "🎯", label: "人岗匹配", desc: "对比职位要求，量化匹配度" },
            { icon: "✏️", label: "简历优化", desc: "检测空洞动词，逐条改写" },
            { icon: "🎤", label: "模拟面试", desc: "多轮问答，自动出评估报告" },
            { icon: "💡", label: "职业咨询", desc: "RAG 知识库，回答求职疑问" },
            { icon: "🔌", label: "API 调试", desc: "可视化面板，实时调试接口" },
          ].map((f) => (
            <div key={f.label} style={{
              padding: "10px", borderRadius: 8,
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.03)",
            }}>
              <div style={{ fontSize: 16, marginBottom: 2 }}>{f.icon}</div>
              <div style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.7)", marginBottom: 1 }}>{f.label}</div>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)" }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── 技术栈 ── */}
      <div style={{
        position: "relative", zIndex: 5,
        maxWidth: 800, margin: "0 auto", padding: "36px 24px 0",
        width: "100%",
      }}>
        <div style={{ textAlign: "center", marginBottom: "20px" }}>
          <div style={{
            display: "inline-block", padding: "3px 12px", borderRadius: 100,
            background: "rgba(74,143,212,0.1)", border: "1px solid rgba(74,143,212,0.15)",
            fontSize: 10, color: "rgba(255,255,255,0.5)", marginBottom: 12,
            letterSpacing: "1px",
          }}>
            技术栈
          </div>
        </div>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 10,
        }}>
          {[
            {
              category: "前端", techs: [
                { name: "Next.js 16", desc: "React 框架", color: "#4a8fd4" },
                { name: "TypeScript", desc: "类型安全", color: "#3178c6" },
                { name: "Tailwind CSS", desc: "样式系统", color: "#06b6d4" },
              ],
            },
            {
              category: "后端", techs: [
                { name: "Python 3.13", desc: "核心语言", color: "#3776ab" },
                { name: "FastAPI", desc: "异步框架", color: "#4ad47a" },
                { name: "LangGraph", desc: "Agent 编排", color: "#d4804a" },
              ],
            },
            {
              category: "AI / 数据", techs: [
                { name: "DeepSeek API", desc: "大语言模型", color: "#d44a8a" },
                { name: "ChromaDB", desc: "向量数据库", color: "#e8a040" },
                { name: "PyMuPDF", desc: "PDF 解析", color: "#8a4ad4" },
              ],
            },
            {
              category: "DevOps", techs: [
                { name: "Docker", desc: "容器化部署", color: "#2496ed" },
                { name: "GitHub", desc: "版本控制", color: "#ccc" },
                { name: "SSE 流式", desc: "实时推送", color: "#4ad4a0" },
              ],
            },
          ].map((group) => (
            <div key={group.category} style={{
              padding: "14px 16px", borderRadius: 12,
              background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)",
            }}>
              <div style={{
                fontSize: 10, fontWeight: 600, color: "rgba(255,255,255,0.3)",
                marginBottom: 10, textTransform: "uppercase", letterSpacing: "1px",
              }}>
                {group.category}
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {group.techs.map((t) => (
                  <div key={t.name} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{
                      width: 6, height: 6, borderRadius: "50%",
                      background: t.color, flexShrink: 0,
                      boxShadow: `0 0 6px ${t.color}40`,
                    }} />
                    <div style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.8)", flex: 1 }}>{t.name}</div>
                    <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)" }}>{t.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Features Grid ── */}
      <div style={{
        position: "relative", zIndex: 5,
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: 10, padding: "40px 28px 48px",
        maxWidth: 900, margin: "0 auto", width: "100%",
      }}>
        {FEATURES.map((f, i) => (
            <div key={f.title} style={{
              padding: "18px", borderRadius: 14,
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.04)",
              transition: "all 0.25s cubic-bezier(0.34,1.56,0.64,1)",
              cursor: "default",
              animation: `fadeUp 0.4s ease-out ${0.3 + i * 0.06}s both`,
              position: "relative", overflow: "hidden",
            }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                e.currentTarget.style.transform = "translateY(-4px) scale(1.01)";
                e.currentTarget.style.borderColor = `${f.color}30`;
                e.currentTarget.style.boxShadow = `0 12px 40px rgba(0,0,0,0.3), 0 0 0 1px ${f.color}15`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "";
                e.currentTarget.style.transform = "";
                e.currentTarget.style.borderColor = "";
                e.currentTarget.style.boxShadow = "";
              }}>
              <div style={{
                width: 36, height: 36, borderRadius: 10,
                background: `${f.color}12`, display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 18, marginBottom: 10,
              }}>{f.icon}</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.85)", marginBottom: 4 }}>{f.title}</div>
              <div style={{ fontSize: 10.5, color: "rgba(255,255,255,0.35)", lineHeight: 1.5 }}>{f.desc}</div>
            </div>
          ))}
      </div>

      {/* ── Footer ── */}
      <div style={{
        position: "relative", zIndex: 5,
        textAlign: "center", padding: "16px 24px 24px",
        fontSize: 10, color: "rgba(255,255,255,0.12)", letterSpacing: "0.3px",
      }}>
        CareerAI · LangGraph + FastAPI + Next.js · Built with Claude Code
      </div>

      <style>{`
        @keyframes particleFloat0 { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-30px); } }
        @keyframes particleFloat1 { 0%,100% { transform: translateY(0) translateX(0); } 50% { transform: translateY(-20px) translateX(15px); } }
        @keyframes particleFloat2 { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-40px); } }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
      `}</style>
    </div>
  );
}
