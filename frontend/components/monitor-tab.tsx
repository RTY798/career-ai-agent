"use client";

export default function MonitorTab() {
  return (
    <div style={{ display: "flex", gap: 16, height: "100%", alignItems: "center", justifyContent: "center" }}>
      <div className="placeholder-state anim-fade-in" style={{ gap: 12 }}>
        <div className="icon" style={{ fontSize: 48, opacity: 0.4 }}>📊</div>
        <div className="text" style={{ fontSize: 15 }}>暂无监控数据</div>
        <div className="hint" style={{ maxWidth: 320 }}>
          API 调用记录、响应时间、Token 消耗等性能数据将在系统运行后自动生成。
          去「简历分析」或「模拟面试」发送几条消息，就能在这里看到效果。
        </div>
      </div>
    </div>
  );
}
