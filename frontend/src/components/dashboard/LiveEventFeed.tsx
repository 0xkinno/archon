"use client";

import React, { useEffect, useState, useRef } from "react";
import { WebSocketEvent } from "@/lib/types";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  ShieldAlert,
  BrainCircuit,
  Bot,
  Zap,
  Radio,
  Pause,
  Play,
  Trash2,
} from "lucide-react";

function getWebSocketUrl(): string {
  if (process.env.NEXT_PUBLIC_WS_URL) {
    return process.env.NEXT_PUBLIC_WS_URL;
  }
  if (process.env.NEXT_PUBLIC_API_URL) {
    const apiBase = process.env.NEXT_PUBLIC_API_URL.replace(/^http/, "ws");
    return `${apiBase.replace(/\/$/, "")}/ws`;
  }
  return "ws://localhost:8000/ws";
}

interface LiveEventFeedProps {
  onNewEvent?: (event: WebSocketEvent) => void;
}

export const LiveEventFeed: React.FC<LiveEventFeedProps> = ({ onNewEvent }) => {
  const [events, setEvents] = useState<WebSocketEvent[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const feedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    function connect() {
      try {
        const targetUrl = getWebSocketUrl();
        ws = new WebSocket(targetUrl);

        ws.onopen = () => {
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data: WebSocketEvent = JSON.parse(event.data);
            if (!isPaused) {
              setEvents((prev) => [data, ...prev.slice(0, 49)]);
            }
            if (onNewEvent) {
              onNewEvent(data);
            }
          } catch (e) {
            console.error("WS Parse error:", e);
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          reconnectTimeout = setTimeout(connect, 3000);
        };

        ws.onerror = () => {
          setIsConnected(false);
        };
      } catch (err) {
        console.error("WS connection error:", err);
      }
    }

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [isPaused, onNewEvent]);

  const getEventBadge = (type: string) => {
    if (type.startsWith("incident")) return { color: "text-red-400 bg-red-500/10 border-red-500/30", icon: AlertTriangle };
    if (type.startsWith("agent")) return { color: "text-purple-400 bg-purple-500/10 border-purple-500/30", icon: Bot };
    if (type.startsWith("approval")) return { color: "text-amber-400 bg-amber-500/10 border-amber-500/30", icon: CheckCircle };
    if (type.startsWith("memory")) return { color: "text-purple-300 bg-purple-500/10 border-purple-500/30", icon: BrainCircuit };
    if (type.startsWith("armor")) return { color: "text-rose-400 bg-rose-500/10 border-rose-500/30", icon: ShieldAlert };
    return { color: "text-blue-400 bg-blue-500/10 border-blue-500/30", icon: Activity };
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-white/10 flex flex-col h-[520px]">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${isConnected ? "bg-emerald-400 pulse-dot-green" : "bg-red-400"}`} />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Live Stream Feed
          </h3>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`p-1.5 rounded-lg border transition-colors ${
              isPaused
                ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                : "bg-white/5 text-slate-400 hover:text-white border-white/10"
            }`}
            title={isPaused ? "Resume Live Feed" : "Pause Stream"}
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => setEvents([])}
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/10 transition-colors"
            title="Clear Stream"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Events List */}
      <div ref={feedRef} className="flex-1 overflow-y-auto space-y-2 pr-1">
        {events.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs text-center p-6 space-y-2">
            <Radio className="w-8 h-8 text-slate-600 animate-pulse" />
            <div>WebSocket listening for real-time fleet events...</div>
            <div className="text-[10px] text-slate-600">Simulate a storm response to trigger stream.</div>
          </div>
        ) : (
          events.map((ev, idx) => {
            const { color, icon: Icon } = getEventBadge(ev.type);
            const timeStr = new Date(ev.timestamp).toLocaleTimeString();

            return (
              <div
                key={idx}
                className="p-3 rounded-lg bg-navy-950/70 border border-white/5 hover:border-white/15 transition-all text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono border ${color}`}>
                    <Icon className="w-3 h-3" />
                    <span>{ev.type}</span>
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">{timeStr}</span>
                </div>

                <div className="text-slate-300 font-mono text-[11px] leading-snug">
                  {typeof ev.data === "object" ? (
                    <span>
                      {ev.data.title ||
                        ev.data.reason ||
                        ev.data.action ||
                        ev.data.message ||
                        JSON.stringify(ev.data).slice(0, 100)}
                    </span>
                  ) : (
                    String(ev.data)
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
