import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#0A0F1E",
          900: "#0F172A",
          800: "#1E293B",
          700: "#334155",
        },
        amber: {
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706",
        },
        agent: {
          commander: "#8B5CF6",
          impact: "#EC4899",
          vendor: "#14B8A6",
          compliance: "#F97316",
          comms: "#3B82F6",
          remediation: "#22C55E",
          memory: "#A78BFA",
        }
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        glow: {
          "0%": { opacity: "0.4", filter: "drop-shadow(0 0 8px rgba(245, 158, 11, 0.4))" },
          "100%": { opacity: "1", filter: "drop-shadow(0 0 16px rgba(245, 158, 11, 0.8))" },
        }
      }
    },
  },
  plugins: [],
};
export default config;
