import React from "react";
import { Hero } from "@/components/landing/Hero";
import { Problem } from "@/components/landing/Problem";
import { Solution } from "@/components/landing/Solution";
import { AgentFleet } from "@/components/landing/AgentFleet";
import { GovernanceLayer } from "@/components/landing/GovernanceLayer";
import { Architecture } from "@/components/landing/Architecture";
import { DemoScenario } from "@/components/landing/DemoScenario";
import { TechStack } from "@/components/landing/TechStack";
import { Footer } from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <main className="min-h-screen flex flex-col justify-between">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 w-full glass-panel border-b border-white/10 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold">
            ⚡
          </span>
          <span className="text-base font-extrabold tracking-wider text-white">ARCHON</span>
        </div>

        <div className="flex items-center gap-4">
          <a
            href="https://github.com/Kingnanaweb3/archon"
            target="_blank"
            rel="noreferrer"
            className="text-xs font-mono text-slate-300 hover:text-white transition-colors hidden sm:block"
          >
            GitHub
          </a>
          <a
            href="/dashboard"
            className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-navy-950 text-xs font-bold transition-all shadow-md shadow-amber-500/10"
          >
            Launch Command Dashboard
          </a>
        </div>
      </header>

      {/* 9 Comprehensive Landing Sections */}
      <Hero />
      <Problem />
      <Solution />
      <AgentFleet />
      <GovernanceLayer />
      <Architecture />
      <DemoScenario />
      <TechStack />
      <Footer />
    </main>
  );
}
