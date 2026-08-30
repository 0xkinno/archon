import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BackgroundGrid } from "../components/BackgroundGrid";
import { GlassCard } from "../components/GlassCard";
import { theme } from "../theme";

export const Scene2_TheProblem: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Camera drift
  const cameraZoom = interpolate(frame, [0, 300], [1.0, 1.05]);

  // Section Header
  const titleOpacity = interpolate(frame, [0, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Ticking Counter: $0 -> $250 Billion
  const counterVal = Math.floor(
    interpolate(frame, [20, 140], [0, 250], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  // Staggered Incident Cards
  const card1Spring = spring({
    frame: frame - 40,
    fps,
    config: { damping: 14, stiffness: 100 },
  });
  const card2Spring = spring({
    frame: frame - 70,
    fps,
    config: { damping: 14, stiffness: 100 },
  });
  const card3Spring = spring({
    frame: frame - 100,
    fps,
    config: { damping: 14, stiffness: 100 },
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
        padding: "60px 80px",
        transform: `scale(${cameraZoom})`,
      }}
    >
      <BackgroundGrid pulseColor={theme.colors.rose} gridOpacity={0.2} />

      {/* Header Tag */}
      <div
        style={{
          opacity: titleOpacity,
          textAlign: "center",
          marginBottom: 32,
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 16px",
            borderRadius: 20,
            background: "rgba(244, 63, 94, 0.15)",
            border: "1px solid rgba(244, 63, 94, 0.4)",
            color: theme.colors.rose,
            fontFamily: theme.fonts.mono,
            fontSize: 14,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            marginBottom: 16,
          }}
        >
          <span style={{ fontSize: 18 }}>⚠</span> Critical Operational Reality
        </div>

        <h2
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 52,
            fontWeight: 900,
            color: theme.colors.textPrimary,
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          Physical Campus Operations Are Fractured.
        </h2>
      </div>

      {/* Main Grid: Stat Box + 3 Cascading Failure Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1.3fr",
          gap: 32,
          width: "100%",
          maxWidth: 1400,
        }}
      >
        {/* Left Column: Big Cost Stat */}
        <GlassCard
          borderColor="rgba(244, 63, 94, 0.4)"
          glowColor={theme.colors.roseGlow}
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            textAlign: "center",
            padding: 48,
          }}
        >
          <span
            style={{
              fontFamily: theme.fonts.mono,
              fontSize: 16,
              color: theme.colors.textSecondary,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              marginBottom: 12,
            }}
          >
            Annual Cost of Unplanned Facility Downtime
          </span>

          <div
            style={{
              fontFamily: theme.fonts.mono,
              fontSize: 76,
              fontWeight: 900,
              color: theme.colors.rose,
              lineHeight: 1,
              letterSpacing: "-0.04em",
              textShadow: "0 0 30px rgba(244, 63, 94, 0.5)",
            }}
          >
            ${counterVal}B+
          </div>

          <p
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 18,
              color: theme.colors.textSecondary,
              marginTop: 24,
              lineHeight: 1.5,
              maxWidth: 420,
            }}
          >
            When veteran facility directors retire, decades of institutional knowledge
            disappear with them — leaving teams reacting in the dark.
          </p>
        </GlassCard>

        {/* Right Column: Cascading Failure Timeline */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Failure 1 */}
          <div
            style={{
              transform: `translateX(${interpolate(card1Spring, [0, 1], [60, 0])}px)`,
              opacity: interpolate(card1Spring, [0, 1], [0, 1]),
            }}
          >
            <GlassCard
              borderColor="rgba(244, 63, 94, 0.3)"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                padding: "20px 24px",
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 10,
                  backgroundColor: "rgba(244, 63, 94, 0.2)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 22,
                  color: theme.colors.rose,
                  fontWeight: "bold",
                }}
              >
                P1
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span
                    style={{
                      fontFamily: theme.fonts.sans,
                      fontSize: 18,
                      fontWeight: 700,
                      color: theme.colors.textPrimary,
                    }}
                  >
                    Building C: Sub-Basement Water Main Breach
                  </span>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.rose }}>
                    02:14 AM
                  </span>
                </div>
                <p style={{ fontFamily: theme.fonts.sans, fontSize: 14, color: theme.colors.textSecondary, margin: "4px 0 0" }}>
                  Pressure loss to 12 PSI. Threatens primary chiller cross-tie to hospital network.
                </p>
              </div>
            </GlassCard>
          </div>

          {/* Failure 2 */}
          <div
            style={{
              transform: `translateX(${interpolate(card2Spring, [0, 1], [60, 0])}px)`,
              opacity: interpolate(card2Spring, [0, 1], [0, 1]),
            }}
          >
            <GlassCard
              borderColor="rgba(245, 158, 11, 0.3)"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                padding: "20px 24px",
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 10,
                  backgroundColor: "rgba(245, 158, 11, 0.2)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 22,
                  color: theme.colors.amber,
                  fontWeight: "bold",
                }}
              >
                P2
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span
                    style={{
                      fontFamily: theme.fonts.sans,
                      fontSize: 18,
                      fontWeight: 700,
                      color: theme.colors.textPrimary,
                    }}
                  >
                    Hospital Zone 3 (NICU): HVAC Thermal Drift
                  </span>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.amber }}>
                    02:16 AM
                  </span>
                </div>
                <p style={{ fontFamily: theme.fonts.sans, fontSize: 14, color: theme.colors.textSecondary, margin: "4px 0 0" }}>
                  Chilled water flow cut. Ambient temperature rising +4.2°F/hr without bypass valve V-104.
                </p>
              </div>
            </GlassCard>
          </div>

          {/* Failure 3 */}
          <div
            style={{
              transform: `translateX(${interpolate(card3Spring, [0, 1], [60, 0])}px)`,
              opacity: interpolate(card3Spring, [0, 1], [0, 1]),
            }}
          >
            <GlassCard
              borderColor="rgba(148, 163, 184, 0.3)"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                padding: "20px 24px",
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 10,
                  backgroundColor: "rgba(148, 163, 184, 0.2)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 22,
                  color: theme.colors.textPrimary,
                  fontWeight: "bold",
                }}
              >
                P3
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span
                    style={{
                      fontFamily: theme.fonts.sans,
                      fontSize: 18,
                      fontWeight: 700,
                      color: theme.colors.textPrimary,
                    }}
                  >
                    Atlas Elevator: Contracted No-Show on P1 Emergency
                  </span>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.textMuted }}>
                    02:18 AM
                  </span>
                </div>
                <p style={{ fontFamily: theme.fonts.sans, fontSize: 14, color: theme.colors.textSecondary, margin: "4px 0 0" }}>
                  No automated vendor failover or penalty triggers in traditional facility software.
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
};
