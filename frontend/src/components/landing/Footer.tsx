"use client";

import React from "react";
import Link from "next/link";
import { ShieldAlert, Github, ExternalLink, Heart } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="py-16 px-4 sm:px-6 lg:px-8 border-t border-white/10 bg-navy-950 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
        {/* Brand Column */}
        <div className="space-y-4 md:col-span-2">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold">
              <ShieldAlert className="w-5 h-5" />
            </span>
            <span className="text-base font-extrabold tracking-wider text-white">ARCHON</span>
          </div>
          <p className="text-slate-400 text-xs leading-relaxed max-w-sm">
            Institutional Intelligence That Never Forgets. Enterprise Incident Intelligence & Operational Resilience Platform built for the All Things Agentic Hackathon (Fortified Enterprise Fleet Track).
          </p>
          <div className="text-[11px] text-slate-500 font-mono">
            Category: Fortified Enterprise Fleet | #AllThingsAgenticHackathon
          </div>
        </div>

        {/* Resources */}
        <div className="space-y-3">
          <div className="font-mono text-white text-xs uppercase font-bold tracking-wider">
            Resources
          </div>
          <ul className="space-y-2">
            <li>
              <Link href="/dashboard" className="hover:text-amber-400 transition-colors">
                Command Dashboard
              </Link>
            </li>
            <li>
              <a
                href="https://github.com/Kingnanaweb3/archon"
                target="_blank"
                rel="noreferrer"
                className="hover:text-amber-400 transition-colors flex items-center gap-1"
              >
                <span>GitHub Repository</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </li>
            <li>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="hover:text-amber-400 transition-colors flex items-center gap-1"
              >
                <span>FastAPI OpenAPI Docs</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </li>
          </ul>
        </div>

        {/* Team & Social */}
        <div className="space-y-3">
          <div className="font-mono text-white text-xs uppercase font-bold tracking-wider">
            Author & Submission
          </div>
          <p className="text-xs text-slate-400">
            Engineered by Kinnoski for the Google Cloud & Devpost Hackathon.
          </p>
          <div className="flex items-center gap-4 pt-2">
            <a
              href="https://github.com/Kingnanaweb3"
              target="_blank"
              rel="noreferrer"
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
            >
              <Github className="w-4 h-4" />
            </a>
            <a
              href="https://x.com/0xkinno"
              target="_blank"
              rel="noreferrer"
              className="text-xs font-mono text-amber-400 hover:underline"
            >
              @0xkinno
            </a>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-8 border-t border-white/5 flex flex-wrap items-center justify-between gap-4 text-slate-500 text-[11px] font-mono">
        <div>(c) 2026 ARCHON Enterprise Operations Platform. Released under MIT License.</div>
        <div>Built with Google ADK 2.6.2 & Gemini 3.5 Flash</div>
      </div>
    </footer>
  );
};
