"use client";

import { useState, useEffect, useRef } from "react";
import type { Role, TabId } from "../lib/types";
import { ROLE_TABS, ROLE_LABELS } from "../lib/types";
import ResumeTab from "../components/resume-tab";
import InterviewTab from "../components/interview-tab";
import MatchTab from "../components/match-tab";
import OptimizeTab from "../components/optimize-tab";
import AdviceTab from "../components/advice-tab";
import QuestionsTab from "../components/questions-tab";
import ArchitectureTab from "../components/architecture-tab";
import ApiTab from "../components/api-tab";
import MonitorTab from "../components/monitor-tab";

const DEFAULT_ROLE: Role = "job_seeker";

export default function AppShell() {
  const [role, setRole] = useState<Role>(DEFAULT_ROLE);
  const [showRoleMenu, setShowRoleMenu] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>("resume");
  const roleMenuRef = useRef<HTMLDivElement>(null);
  const [showApp, setShowApp] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("careerai_role") as Role | null;
    if (saved && ROLE_LABELS[saved]) {
      setRole(saved);
      const tabs = ROLE_TABS[saved];
      const savedTab = localStorage.getItem("careerai_tab") as TabId | null;
      if (savedTab && tabs.some((t) => t.id === savedTab)) setActiveTab(savedTab);
      else if (tabs.length > 0) setActiveTab(tabs[0].id);
    }
    setShowApp(true);
  }, []);

  useEffect(() => { localStorage.setItem("careerai_role", role); }, [role]);
  useEffect(() => { localStorage.setItem("careerai_tab", activeTab); }, [activeTab]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (roleMenuRef.current && !roleMenuRef.current.contains(e.target as Node)) setShowRoleMenu(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const tabs = ROLE_TABS[role];
  const switchRole = (r: Role) => {
    setRole(r); setShowRoleMenu(false);
    setActiveTab(ROLE_TABS[r][0].id);
  };

  return (
    <div className="app-container" style={{ opacity: showApp ? 1 : 0, transition: "opacity 0.4s" }}>
      <header className="app-header">
        <div className="app-header-left">
          <div className="app-logo">🎯</div>
          <div>
            <div className="app-title">CareerAI</div>
            <div className="app-subtitle">AI 求职 Agent 系统</div>
          </div>
        </div>
        <div className="role-selector" ref={roleMenuRef}>
          <button className="role-btn" onClick={() => setShowRoleMenu(!showRoleMenu)}>
            {ROLE_LABELS[role]} <span style={{ fontSize: 9 }}>▾</span>
          </button>
          {showRoleMenu && (
            <div className="role-menu">
              {(Object.keys(ROLE_LABELS) as Role[]).map((r) => (
                <button key={r} className={`role-menu-item${r === role ? " active" : ""}`} onClick={() => switchRole(r)}>
                  {ROLE_LABELS[r]}
                </button>
              ))}
            </div>
          )}
        </div>
      </header>

      <div className="tab-bar-wrapper">
        <div className="tab-bar">
          {tabs.map((tab) => (
            <button key={tab.id} className={`tab-btn${activeTab === tab.id ? " active" : ""}`} onClick={() => setActiveTab(tab.id)}>
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main className="app-main">
        {activeTab === "resume" && <ResumeTab />}
        {activeTab === "interview" && <InterviewTab />}
        {activeTab === "match" && <MatchTab />}
        {activeTab === "optimize" && <OptimizeTab />}
        {activeTab === "advice" && <AdviceTab />}
        {activeTab === "questions" && <QuestionsTab />}
        {activeTab === "architecture" && <ArchitectureTab />}
        {activeTab === "api" && <ApiTab />}
        {activeTab === "monitor" && <MonitorTab />}
      </main>
    </div>
  );
}
