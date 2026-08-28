import React from "react";
import { SEVERITY_CONFIG } from "@/lib/constants";
import { IncidentSeverity } from "@/lib/types";

interface SeverityIndicatorProps {
  severity: IncidentSeverity;
  size?: "sm" | "md" | "lg";
  withPulse?: boolean;
}

export const SeverityIndicator: React.FC<SeverityIndicatorProps> = ({ severity, size = "md", withPulse = false }) => {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.P3;

  const sizeClasses = {
    sm: "text-[10px] px-1.5 py-0.5 font-bold",
    md: "text-xs px-2.5 py-0.5 font-bold",
    lg: "text-sm px-3.5 py-1 font-extrabold",
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border uppercase tracking-wider ${config.badgeBg} ${sizeClasses[size]}`}>
      {withPulse && (
        <span className="relative flex h-2 w-2">
          <span
            className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
            style={{ backgroundColor: config.color }}
          />
          <span className="relative inline-flex rounded-full h-2 w-2" style={{ backgroundColor: config.color }} />
        </span>
      )}
      {config.label}
    </span>
  );
};
