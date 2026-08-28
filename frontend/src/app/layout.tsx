import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "ARCHON | Enterprise Incident Intelligence & Operational Resilience Platform",
  description:
    "Institutional Intelligence That Never Forgets. A governed fleet of 7 AI agents built with Google ADK for the All Things Agentic Hackathon.",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-navy-950 text-slate-100 antialiased selection:bg-amber-500/30 selection:text-amber-200">
        {children}
      </body>
    </html>
  );
}
