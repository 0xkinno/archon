import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

export const ArchonLogo: React.FC<{
  size?: number;
  showText?: boolean;
  delay?: number;
}> = ({ size = 120, showText = true, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);

  const scale = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.8 },
  });

  const opacity = interpolate(adjustedFrame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const rotation = interpolate(adjustedFrame, [0, 60], [-30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const pulse = interpolate(Math.sin((frame + delay) * 0.08), [-1, 1], [0.85, 1.15]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      {/* Hexagonal Shield Logo with Neural Core */}
      <div
        style={{
          position: "relative",
          width: size,
          height: size,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {/* Outer Glow Halo */}
        <div
          style={{
            position: "absolute",
            width: size * 1.5,
            height: size * 1.5,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${theme.colors.blueGlow} 0%, transparent 70%)`,
            transform: `scale(${pulse})`,
            filter: "blur(20px)",
          }}
        />

        {/* SVG Crest */}
        <svg
          width={size}
          height={size}
          viewBox="0 0 120 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{
            transform: `rotate(${rotation}deg)`,
            filter: "drop-shadow(0 0 25px rgba(59, 130, 246, 0.6))",
          }}
        >
          {/* Outer Hexagon */}
          <polygon
            points="60,6 108,30 108,90 60,114 12,90 12,30"
            stroke="url(#blueAmberGrad)"
            strokeWidth="3.5"
            fill="rgba(10, 15, 29, 0.85)"
          />

          {/* Inner Geometric Shield Lines */}
          <polygon
            points="60,20 94,38 94,82 60,100 26,82 26,38"
            stroke="rgba(255, 255, 255, 0.25)"
            strokeWidth="1.5"
            strokeDasharray="4 3"
          />

          {/* Center Neural Node Connections */}
          <line x1="60" y1="20" x2="60" y2="60" stroke={theme.colors.amber} strokeWidth="2.5" />
          <line x1="26" y1="82" x2="60" y2="60" stroke={theme.colors.blue} strokeWidth="2.5" />
          <line x1="94" y1="82" x2="60" y2="60" stroke={theme.colors.emerald} strokeWidth="2.5" />

          {/* Core Energy Sphere */}
          <circle cx="60" cy="60" r="12" fill="url(#coreGrad)" />
          <circle cx="60" cy="60" r="6" fill="#FFFFFF" opacity="0.9" />

          {/* Gradients */}
          <defs>
            <linearGradient id="blueAmberGrad" x1="12" y1="6" x2="108" y2="114" gradientUnits="userSpaceOnUse">
              <stop stopColor="#3B82F6" />
              <stop offset="0.5" stopColor="#60A5FA" />
              <stop offset="1" stopColor="#F59E0B" />
            </linearGradient>
            <radialGradient id="coreGrad" cx="50%" cy="50%" r="50%">
              <stop stopColor="#FFFFFF" />
              <stop offset="0.4" stopColor="#F59E0B" />
              <stop offset="1" stopColor="#3B82F6" />
            </radialGradient>
          </defs>
        </svg>
      </div>

      {showText && (
        <div style={{ marginTop: 24, textAlign: "center" }}>
          <h1
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: size * 0.45,
              fontWeight: 900,
              letterSpacing: "0.22em",
              color: theme.colors.textPrimary,
              margin: 0,
              textTransform: "uppercase",
              background: "linear-gradient(180deg, #FFFFFF 0%, #94A3B8 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              filter: "drop-shadow(0 4px 16px rgba(0,0,0,0.8))",
            }}
          >
            ARCHON
          </h1>
        </div>
      )}
    </div>
  );
};
