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

export const Scene3_SystemArchitecture: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cameraScale = interpolate(frame, [0, 300], [1.0, 1.06]);

  const headerSpring = spring({
    frame: frame - 10,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const fleetSpring = spring({
    frame: frame - 50,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const agents = [
    { name: "incident_commander", role: "Swarm Orchestrator & Triage", color: theme.colors.amber },
    { name: "impact_assessor", role: "Blast Radius & Topology Traversal", color: theme.colors.rose },
    { name: "vendor_coordinator", role: "SLA Scoring & Auto-Dispatch", color: theme.colors.blue },
    { name: "compliance_inspector", role: "Fire/OSHA Regulatory Defense", color: theme.colors.emerald },
    { name: "communications_officer", role: "Multi-Channel Stakeholder Alerts", color: theme.colors.violet },
    { name: "remediation_tracker", role: "Corrective Work Orders & Shifts", color: theme.colors.amberLight },
    { name: "memory_curator", role: "Institutional Wisdom Extraction", color: theme.colors.blueLight },
  ];

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
      <BackgroundGrid pulseColor={theme.colors.blue} gridOpacity={0.22} />

      {/* Header */}
      <div
        style={{
          textAlign: "center",
          opacity: interpolate(headerSpring, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-20, 0])}px)`,
          marginBottom: 28,
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 18px",
            borderRadius: 20,
            background: "rgba(59, 130, 246, 0.15)",
            border: "1px solid rgba(59, 130, 246, 0.4)",
            color: theme.colors.blueLight,
            fontFamily: theme.fonts.mono,
            fontSize: 14,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            marginBottom: 12,
          }}
        >
          Google Enterprise Agent Platform (GEAP)
        </div>

        <h2
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 48,
            fontWeight: 900,
            color: theme.colors.textPrimary,
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          7 Governed Specialist Agents in Autonomous Swarm
        </h2>
      </div>

      {/* 3-Layer Visual Architecture: Governance Firewall -> 7 Agent Fleet -> State & Memory */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1.6fr 1fr",
          gap: 24,
          width: "100%",
          maxWidth: 1550,
          opacity: interpolate(fleetSpring, [0, 1], [0, 1]),
          transform: `scale(${interpolate(fleetSpring, [0, 1], [0.94, 1])})`,
        }}
      >
        {/* Layer 1: Inbound Defense & Governance */}
        <GlassCard
          borderColor="rgba(59, 130, 246, 0.35)"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 16,
            padding: 24,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 20 }}>🛡</span>
            <span
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 16,
                fontWeight: 700,
                color: theme.colors.blueLight,
                textTransform: "uppercase",
              }}
            >
              1. Governance Layer
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div
              style={{
                padding: "12px 14px",
                borderRadius: 8,
                background: "rgba(15, 23, 42, 0.6)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
              }}
            >
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.emerald, fontWeight: 700 }}>
                MODEL ARMOR FIREWALL
              </div>
              <div style={{ fontFamily: theme.fonts.sans, fontSize: 12, color: theme.colors.textSecondary, marginTop: 4 }}>
                16 Injection Signatures • 5 PII Redactions • Tool Poisoning Defense
              </div>
            </div>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: 8,
                background: "rgba(15, 23, 42, 0.6)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
              }}
            >
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.amber, fontWeight: 700 }}>
                AGENT GATEWAY POLICY
              </div>
              <div style={{ fontFamily: theme.fonts.sans, fontSize: 12, color: theme.colors.textSecondary, marginTop: 4 }}>
                $10k Financial Threshold • Domain Scoping • 20-Call Rate Limiting
              </div>
            </div>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: 8,
                background: "rgba(15, 23, 42, 0.6)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
              }}
            >
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.violet, fontWeight: 700 }}>
                ZERO-TRUST IDENTITY
              </div>
              <div style={{ fontFamily: theme.fonts.sans, fontSize: 12, color: theme.colors.textSecondary, marginTop: 4 }}>
                SPIFFE Identifiers • Scoped JWT Claims • Tool Boundary Authorization
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Layer 2: 7 Specialist Agent Swarm */}
        <GlassCard
          borderColor="rgba(245, 158, 11, 0.4)"
          glowColor={theme.colors.amberGlow}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 12,
            padding: 24,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 20 }}>⚡</span>
              <span
                style={{
                  fontFamily: theme.fonts.mono,
                  fontSize: 16,
                  fontWeight: 700,
                  color: theme.colors.amber,
                  textTransform: "uppercase",
                }}
              >
                2. Autonomous Agent Fleet
              </span>
            </div>
            <span style={{ fontFamily: theme.fonts.mono, fontSize: 12, color: theme.colors.emerald }}>
              ● 7 ACTIVE MANIFESTS
            </span>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr",
              gap: 8,
            }}
          >
            {agents.map((agent, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "8px 14px",
                  borderRadius: 8,
                  background: "rgba(15, 23, 42, 0.7)",
                  border: `1px solid ${agent.color}33`,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor: agent.color,
                      boxShadow: `0 0 8px ${agent.color}`,
                    }}
                  />
                  <span
                    style={{
                      fontFamily: theme.fonts.mono,
                      fontSize: 14,
                      fontWeight: 700,
                      color: theme.colors.textPrimary,
                    }}
                  >
                    {agent.name}
                  </span>
                </div>
                <span
                  style={{
                    fontFamily: theme.fonts.sans,
                    fontSize: 12,
                    color: theme.colors.textSecondary,
                  }}
                >
                  {agent.role}
                </span>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Layer 3: Persistence & Observability */}
        <GlassCard
          borderColor="rgba(16, 185, 129, 0.35)"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 16,
            padding: 24,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 20 }}>🧠</span>
            <span
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 16,
                fontWeight: 700,
                color: theme.colors.emeraldLight,
                textTransform: "uppercase",
              }}
            >
              3. State & Memory
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div
              style={{
                padding: "12px 14px",
                borderRadius: 8,
                background: "rgba(15, 23, 42, 0.6)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
              }}
            >
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.violet, fontWeight: 700 }}>
                VERTEX MEMORY BANK
              </div>
              <div style={{ fontFamily: theme.fonts.sans, fontSize: 12, color: theme.colors.textSecondary, marginTop: 4 }}>
                Semantic Vector Precedents • Decadal Building Quirks • Vendor Scorecards
              </div>
            </div>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: 8,
                background: "rgba(15, 23, 42, 0.6)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
              }}
            >
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.emerald, fontWeight: 700 }}>
                CLOUD FIRESTORE LEDGER
              </div>
              <div style={{ fontFamily: theme.fonts.sans, fontSize: 12, color: theme.colors.textSecondary, marginTop: 4 }}>
                Append-Only Audit Ledger • Real-time Collections • Zero Data Loss
              </div>
            </div>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: 8,
                background: "rgba(15, 23, 42, 0.6)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
              }}
            >
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: theme.colors.blue, fontWeight: 700 }}>
                OPENTELEMETRY TRACING
              </div>
              <div style={{ fontFamily: theme.fonts.sans, fontSize: 12, color: theme.colors.textSecondary, marginTop: 4 }}>
                Distributed Spans • Multi-Agent Turn Handoffs • Full Auditability
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
