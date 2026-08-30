import React from "react";
import { theme } from "../theme";

export const GlassCard: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
  borderColor?: string;
  glowColor?: string;
}> = ({ children, style, borderColor = theme.colors.border, glowColor }) => {
  return (
    <div
      style={{
        backgroundColor: theme.colors.bgCard,
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        border: `1px solid ${borderColor}`,
        borderRadius: 16,
        padding: 24,
        boxShadow: glowColor
          ? `0 20px 50px rgba(0, 0, 0, 0.6), 0 0 35px ${glowColor}`
          : "0 20px 50px rgba(0, 0, 0, 0.6)",
        position: "relative",
        overflow: "hidden",
        ...style,
      }}
    >
      {/* Subtle top light reflection */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: "10%",
          right: "10%",
          height: 1,
          background: "linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent)",
        }}
      />
      {children}
    </div>
  );
};
