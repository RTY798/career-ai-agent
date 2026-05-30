import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerAI — AI 求职 Agent 系统",
  description: "基于 LangGraph 的多 Agent 智能求职助手 — 简历分析/人岗匹配/模拟面试/职业咨询",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
