import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Img,
  staticFile,
} from "remotion";
import { BackgroundGrid } from "../components/BackgroundGrid";
import { GlassCard } from "../components/GlassCard";
import { theme } from "../theme";

export const Scene4_WorkflowExecution: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 3D Perspective push
  const cameraRotateX = interpolate(frame, [0, 360], [12, 4]);
  const cameraScale = interpolate(frame, [0, 360], [0.95, 1.04]);

  // Header spring
  const headerSpring = spring({
    frame: frame - 10,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Simulated button click at frame 45
  const isClicked = frame > 45;
  const clickSpring = spring({
    frame: frame - 45,
    fps,
    config: { damping: 12, stiffness: 140 },
  });

  // Telemetry stream pop-ins
  const log1 = frame > 60;
  const log2 = frame > 110;
  const log3 = frame > 160;
  const log4 = frame > 210;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "30px 50px",
      }}
    >
      <BackgroundGrid pulseColor={theme.colors.emerald} gridOpacity={0.25} />

      {/* Header */}
      <div
        style={{
          textAlign: "center",
          opacity: interpolate(headerSpring, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-20, 0])}px)`,
          marginBottom: 20,
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "5px 16px",
            borderRadius: 20,
            background: "rgba(16, 185, 129, 0.15)",
            border: "1px solid rgba(16, 185, 129, 0.4)",
            color: theme.colors.emerald,
            fontFamily: theme.fonts.mono,
            fontSize: 13,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            marginBottom: 8,
          }}
        >
          Live Multi-Agent Telemetry Stream
        </div>

        <h2
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 44,
            fontWeight: 900,
            color: theme.colors.textPrimary,
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          Cascading Storm Scenario Orchestration
        </h2>
      </div>

      {/* Main 3D Stage: Real UI on Left + Live Agent Stream on Right */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.4fr 1fr",
          gap: 24,
          width: "100%",
          maxWidth: 1600,
          perspective: 1200,
          transform: `scale(${cameraScale})`,
        }}
      >
        {/* Real Product Dashboard View with 3D Tilt */}
        <div
          style={{
            transform: `rotateX(${cameraRotateX}deg) rotateY(-4deg)`,
            transformStyle: "preserve-3d",
            borderRadius: 16,
            overflow: "hidden",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            boxShadow: "0 30px 70px rgba(0, 0, 0, 0.8), 0 0 40px rgba(59, 130, 246, 0.3)",
            position: "relative",
          }}
        >
          <Img
            src={staticFile(isClicked ? "real_dashboard_simulating.png" : "real_dashboard_overview.png")}
            style={{
              width: "100%",
              height: "auto",
              display: "block",
            }}
          />

          {/* Trigger Banner Overlay */}
          <div
            style={{
              position: "absolute",
              top: 18,
              right: 18,
              padding: "8px 16px",
              borderRadius: 8,
              background: isClicked ? "rgba(16, 185, 129, 0.9)" : "rgba(245, 158, 11, 0.9)",
              color: "#000",
              fontFamily: theme.fonts.mono,
              fontSize: 13,
              fontWeight: 800,
              display: "flex",
              alignItems: "center",
              gap: 8,
              boxShadow: "0 4px 15px rgba(0,0,0,0.5)",
              transform: isClicked ? `scale(${interpolate(clickSpring, [0, 1], [0.9, 1])})` : "none",
            }}
          >
            <span>{isClicked ? "● SWARM RUNNING" : "▶ SIMULATE STORM"}</span>
          </div>
        </div>

        {/* Live Event Stream Terminal */}
        <GlassCard
          borderColor="rgba(16, 185, 129, 0.4)"
          glowColor={theme.colors.emeraldGlow}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 12,
            padding: 22,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: 10 }}>
            <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.emerald, fontWeight: 700 }}>
              LIVE AGENT FEED (WEBSOCKET)
            </span>
            <span style={{ fontFamily: theme.fonts.mono, fontSize: 12, color: theme.colors.textMuted }}>
              ws://127.0.0.1:8000/ws
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10, overflow: "hidden" }}>
            {log1 && (
              <div
                style={{
                  padding: "10px 14px",
                  borderRadius: 8,
                  background: "rgba(244, 63, 94, 0.15)",
                  border: "1px solid rgba(244, 63, 94, 0.3)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 12, color: theme.colors.rose, fontWeight: 700 }}>
                    [02:14:01] P1 SIGNAL INGESTION
                  </span>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>BMS Webhook</span>
                </div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textPrimary, marginTop: 3 }}>
                  Building C sub-basement water main breach (40 PSI drop).
                </div>
              </div>
            )}

            {log2 && (
              <div
                style={{
                  padding: "10px 14px",
                  borderRadius: 8,
                  background: "rgba(245, 158, 11, 0.15)",
                  border: "1px solid rgba(245, 158, 11, 0.3)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 12, color: theme.colors.amber, fontWeight: 700 }}>
                    [02:14:02] incident_commander
                  </span>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>Google ADK</span>
                </div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textPrimary, marginTop: 3 }}>
                  Classified severity P1. Delegating to impact_assessor and vendor_coordinator.
                </div>
              </div>
            )}

            {log3 && (
              <div
                style={{
                  padding: "10px 14px",
                  borderRadius: 8,
                  background: "rgba(59, 130, 246, 0.15)",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 12, color: theme.colors.blueLight, fontWeight: 700 }}>
                    [02:14:03] impact_assessor
                  </span>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>Topology Tool</span>
                </div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textPrimary, marginTop: 3 }}>
                  Traversed building dependency graph: Hospital NICU chiller loop compromised.
                </div>
              </div>
            )}

            {log4 && (
              <div
                style={{
                  padding: "10px 14px",
                  borderRadius: 8,
                  background: "rgba(16, 185, 129, 0.15)",
                  border: "1px solid rgba(16, 185, 129, 0.3)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 12, color: theme.colors.emerald, fontWeight: 700 }}>
                    [02:14:04] vendor_coordinator
                  </span>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>Auto-Dispatch</span>
                </div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textPrimary, marginTop: 3 }}>
                  Dispatched Cascade Industrial Plumbing (Score: 94, ETA: 1.2 hrs).
                </div>
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
