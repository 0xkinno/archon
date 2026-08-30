import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BackgroundGrid } from "../components/BackgroundGrid";
import { ArchonLogo } from "../components/ArchonLogo";
import { theme } from "../theme";

export const Scene1_BrandReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Subtle camera push forward
  const cameraScale = interpolate(frame, [0, 300], [1.0, 1.08]);

  // Kinetic Tagline Reveal
  const taglineSpring = spring({
    frame: frame - 40,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const taglineOpacity = interpolate(frame, [40, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Subtitle Reveal
  const subOpacity = interpolate(frame, [80, 110], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Badges Reveal
  const badgeSpring = spring({
    frame: frame - 120,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Rotating telemetry rings in background
  const ringRotation = interpolate(frame, [0, 300], [0, 90]);
  const ringRotationReverse = interpolate(frame, [0, 300], [0, -60]);

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
        transform: `scale(${cameraScale})`,
      }}
    >
      <BackgroundGrid pulseColor={theme.colors.blue} gridOpacity={0.25} />

      {/* Rotating Background HUD Geometry */}
      <div
        style={{
          position: "absolute",
          width: 800,
          height: 800,
          borderRadius: "50%",
          border: "1px dashed rgba(59, 130, 246, 0.2)",
          transform: `rotate(${ringRotation}deg)`,
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          border: "1px dotted rgba(245, 158, 11, 0.25)",
          transform: `rotate(${ringRotationReverse}deg)`,
          pointerEvents: "none",
        }}
      />

      {/* Main Logo Lockup */}
      <ArchonLogo size={160} showText={true} delay={10} />

      {/* Kinetic Tagline */}
      <div
        style={{
          marginTop: 36,
          opacity: taglineOpacity,
          transform: `translateY(${interpolate(taglineSpring, [0, 1], [30, 0])}px)`,
          textAlign: "center",
          maxWidth: 1200,
          padding: "0 40px",
        }}
      >
        <h2
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 44,
            fontWeight: 800,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: theme.colors.textPrimary,
            margin: 0,
            lineHeight: 1.2,
          }}
        >
          Institutional Intelligence{" "}
          <span
            style={{
              background: "linear-gradient(90deg, #F59E0B, #60A5FA)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            That Never Forgets.
          </span>
        </h2>

        {/* Subtitle */}
        <p
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 22,
            fontWeight: 400,
            color: theme.colors.textSecondary,
            marginTop: 14,
            opacity: subOpacity,
            letterSpacing: "0.03em",
          }}
        >
          A Governed Multi-Agent Fleet for Physical Campus Operations & Resilience
        </p>
      </div>

      {/* Engineering Badges */}
      <div
        style={{
          display: "flex",
          gap: 16,
          marginTop: 48,
          opacity: interpolate(frame, [120, 150], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          transform: `scale(${badgeSpring})`,
        }}
      >
        {[
          { label: "Google ADK 2.6.2", color: theme.colors.blue },
          { label: "Gemini 3.5 Flash", color: theme.colors.amber },
          { label: "Vertex AI Memory Bank", color: theme.colors.violet },
          { label: "Google Cloud Firestore", color: theme.colors.emerald },
        ].map((badge, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 18px",
              borderRadius: 30,
              background: "rgba(15, 23, 42, 0.8)",
              border: `1px solid ${badge.color}55`,
              boxShadow: `0 4px 20px ${badge.color}22`,
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: badge.color,
                boxShadow: `0 0 10px ${badge.color}`,
              }}
            />
            <span
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 15,
                fontWeight: 600,
                color: theme.colors.textPrimary,
                letterSpacing: "0.02em",
              }}
            >
              {badge.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
