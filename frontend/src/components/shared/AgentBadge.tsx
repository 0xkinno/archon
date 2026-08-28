import React from "react";
import { AGENT_DOMAINS } from "@/lib/constants";
import { ShieldAlert, Network, Truck, FileCheck, Radio, CheckSquare, BrainCircuit, Bot } from "lucide-react";

interface AgentBadgeProps {
  agentName: string;
  showIcon?: boolean;
  size?: "sm" | "md" | "lg";
}

const ICONS: Record<string, any> = {
  incident_commander: ShieldAlert,
  impact_assessor: Network,
  vendor_coordinator: Truck,
  compliance_inspector: FileCheck,
  communications_officer: Radio,
  remediation_tracker: CheckSquare,
  memory_curator: BrainCircuit,
};

export const AgentBadge: React.FC<AgentBadgeProps> = ({ agentName, showIcon = true, size = "md" }) => {
  // Normalize agent key
  const key = agentName.replace("spiffe://archon.campus/agent/", "").toLowerCase();
  const config = AGENT_DOMAINS[key] || {
    name: agentName,
    color: "#94A3B8",
    bgLight: "rgba(148, 163, 184, 0.15)",
    iconName: "Bot",
  };
  const IconComponent = ICONS[key] || Bot;

  const sizeClasses = {
    sm: "text-xs px-2 py-0.5 gap-1",
    md: "text-xs px-2.5 py-1 gap-1.5 font-medium",
    lg: "text-sm px-3.5 py-1.5 gap-2 font-semibold",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border transition-all ${sizeClasses[size]}`}
      style={{
        backgroundColor: config.bgLight,
        borderColor: `${config.color}40`,
        color: config.color,
      }}
    >
      {showIcon && <IconComponent className={size === "sm" ? "w-3 h-3" : size === "lg" ? "w-4 h-4" : "w-3.5 h-3.5"} />}
      <span>{config.name}</span>
    </span>
  );
};
