"use client";

import { useState, lazy, Suspense } from "react";
import LandingPage from "../components/landing-page";

const AppShell = lazy(() => import("../components/app-shell"));

export default function Home() {
  const [entered, setEntered] = useState(false);

  if (!entered) {
    return <LandingPage onEnter={() => setEntered(true)} />;
  }

  return (
    <Suspense fallback={
      <div style={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#0f0c29", color: "rgba(255,255,255,0.6)", fontSize: 14 }}>
        加载中...
      </div>
    }>
      <AppShell />
    </Suspense>
  );
}
