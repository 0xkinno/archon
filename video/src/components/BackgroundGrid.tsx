import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { theme } from "../theme";

export const BackgroundGrid: React.FC<{
  pulseColor?: string;
  gridOpacity?: number;
}> = ({ pulseColor = theme.colors.blue, gridOpacity = 0.18 }) => {
  const frame = useCurrentFrame();

  const translateY = interpolate(frame % 300, [0, 300], [0, 40]);
  const glowPulse = interpolate(Math.sin(frame * 0.05), [-1, 1], [0.6, 1.0]);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundColor: theme.colors.bg,
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      {/* Radial Gradient Ambient Lighting */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 1400,
          height: 900,
          background: `radial-gradient(ellipse at center, ${pulseColor}22 0%, ${theme.colors.navy}00 70%)`,
          filter: "blur(120px)",
          opacity: glowPulse,
        }}
      />

      {/* Secondary Ambient Accent */}
      <div
        style={{
          position: "absolute",
          bottom: "-10%",
          right: "10%",
          width: 900,
          height: 600,
          background: `radial-gradient(ellipse at center, ${theme.colors.amber}15 0%, transparent 70%)`,
          filter: "blur(100px)",
        }}
      />

      {/* 3D Perspective Grid */}
      <div
        style={{
          position: "absolute",
          inset: "-50%",
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, ${gridOpacity}) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, ${gridOpacity}) 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
          transform: `perspective(1000px) rotateX(45deg) translateY(${translateY}px)`,
          maskImage: "radial-gradient(ellipse at 50% 60%, black 20%, transparent 75%)",
          WebkitMaskImage: "radial-gradient(ellipse at 50% 60%, black 20%, transparent 75%)",
        }}
      />

      {/* Top & Bottom Vignette Mask */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle at center, transparent 35%, rgba(2, 4, 9, 0.85) 100%)",
        }}
      />
    </div>
  );
};
