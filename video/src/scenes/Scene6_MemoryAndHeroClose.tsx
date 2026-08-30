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
import { ArchonLogo } from "../components/ArchonLogo";
import { GlassCard } from "../components/GlassCard";
import { theme } from "../theme";

export const Scene6_MemoryAndHeroClose: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cameraScale = interpolate(frame, [0, 270], [1.0, 1.06]);

  // Stage 1: Memory Bank Precedent (0 - 130 frames)
  // Stage 2: Grand Hero Finale (130 - 270 frames)
  const isFinalLogo = frame > 130;

  const memorySpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const heroSpring = spring({
    frame: frame - 130,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

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
        padding: "40px 60px",
        transform: `scale(${cameraScale})`,
      }}
    >
      <BackgroundGrid pulseColor={theme.colors.amber} gridOpacity={0.25} />

      {!isFinalLogo ? (
        /* Stage 1: Memory Bank Retrieval */
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "100%",
            maxWidth: 1300,
            transform: `scale(${memorySpring})`,
            opacity: interpolate(frame, [0, 20], [0, 1]),
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 18px",
              borderRadius: 20,
              background: "rgba(245, 158, 11, 0.15)",
              border: "1px solid rgba(245, 158, 11, 0.4)",
              color: theme.colors.amber,
              fontFamily: theme.fonts.mono,
              fontSize: 14,
              fontWeight: 700,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              marginBottom: 16,
            }}
          >
            Institutional Wisdom Continuity
          </div>

          <h2
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 46,
              fontWeight: 900,
              color: theme.colors.textPrimary,
              margin: "0 0 28px 0",
              textAlign: "center",
            }}
          >
            Decades of Building Lore Stored in Vertex Memory Bank
          </h2>

          <GlassCard
            borderColor="rgba(245, 158, 11, 0.4)"
            glowColor={theme.colors.amberGlow}
            style={{
              width: "100%",
              padding: 32,
              display: "flex",
              flexDirection: "column",
              gap: 20,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ fontSize: 24 }}>🧠</span>
                <div>
                  <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.textMuted }}>
                    SEMANTIC VECTOR PRECEDENT QUERY
                  </div>
                  <div style={{ fontFamily: theme.fonts.mono, fontSize: 18, fontWeight: 700, color: theme.colors.amberLight }}>
                    "Building F panel B3 humidity"
                  </div>
                </div>
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "6px 16px",
                  borderRadius: 20,
                  backgroundColor: "rgba(16, 185, 129, 0.2)",
                  border: `1px solid ${theme.colors.emerald}`,
                  color: theme.colors.emerald,
                  fontFamily: theme.fonts.mono,
                  fontSize: 14,
                  fontWeight: 800,
                }}
              >
                ✓ RELEVANCE SCORE: 1.00
              </div>
            </div>

            <div
              style={{
                background: "rgba(15, 23, 42, 0.8)",
                borderRadius: 10,
                padding: 20,
                border: "1px solid rgba(255, 255, 255, 0.08)",
                fontFamily: theme.fonts.sans,
                fontSize: 16,
                color: theme.colors.textPrimary,
                lineHeight: 1.6,
              }}
            >
              <strong style={{ color: theme.colors.amber }}>Historical Lesson Retrieved:</strong> Building F electrical panel B3 has tripped 5 times during high-humidity periods (&gt;80%). Moisture infiltration through east wall conduit penetration.
              <div style={{ marginTop: 8, color: theme.colors.emerald, fontFamily: theme.fonts.mono, fontSize: 14 }}>
                → Recommended Action: Deploy industrial dehumidifier. Last vendor: Sparks Electric (VND-002, 1.8h arrival). Estimated fix: $12,000.
              </div>
            </div>
          </GlassCard>
        </div>
      ) : (
        /* Stage 2: Grand Hero Finale */
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",
            transform: `scale(${heroSpring})`,
            opacity: interpolate(frame, [130, 150], [0, 1]),
          }}
        >
          <ArchonLogo size={150} showText={true} delay={0} />

          <h2
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 38,
              fontWeight: 800,
              color: theme.colors.textPrimary,
              margin: "24px 0 10px 0",
              letterSpacing: "0.04em",
              textTransform: "uppercase",
            }}
          >
            Institutional Intelligence That Never Forgets.
          </h2>

          <p
            style={{
              fontFamily: theme.fonts.mono,
              fontSize: 17,
              color: theme.colors.textSecondary,
              margin: 0,
              letterSpacing: "0.02em",
            }}
          >
            Fortified Enterprise Fleet Track • All Things Agentic Hackathon
          </p>

          {/* Key Stat Highlights */}
          <div
            style={{
              display: "flex",
              gap: 20,
              marginTop: 36,
            }}
          >
            {[
              { label: "Autonomous Agents", val: "7 Specialists" },
              { label: "Safety Signatures", val: "16 Guardrails" },
              { label: "Live Gemini Latency", val: "5,550 ms" },
              { label: "Test Verification", val: "47 / 47 Passed" },
            ].map((stat, idx) => (
              <div
                key={idx}
                style={{
                  background: "rgba(15, 23, 42, 0.85)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: 12,
                  padding: "12px 24px",
                  boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
                }}
              >
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 20, fontWeight: 900, color: theme.colors.amber }}>
                  {stat.val}
                </div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 12, color: theme.colors.textMuted, marginTop: 2 }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

          <div
            style={{
              marginTop: 32,
              fontFamily: theme.fonts.mono,
              fontSize: 15,
              color: theme.colors.blueLight,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <span>github.com/0xkinno/archon</span>
            <span style={{ color: theme.colors.textMuted }}>•</span>
            <span>archon-app.vercel.app</span>
          </div>
        </div>
      )}
    </div>
  );
};
