"use client";

import React from "react";
import { motion } from "framer-motion";
import { DollarSign, Clock, FileQuestion, AlertOctagon } from "lucide-react";

export const Problem: React.FC = () => {
  const stats = [
    {
      icon: DollarSign,
      stat: "$250B+",
      label: "Annual cost of unplanned facility downtime in the US",
      source: "U.S. Facilities & Infrastructure Council",
    },
    {
      icon: FileQuestion,
      stat: "73%",
      label: "Of campus operational knowledge is undocumented tribal memory",
      source: "Institutional Asset Management Survey",
    },
    {
      icon: Clock,
      stat: "4.2 Hours",
      label: "Average coordination delay for cross-department emergencies",
      source: "Higher Education Operations Benchmark",
    },
  ];

  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 border-t border-white/5 relative">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold uppercase tracking-wider">
            <AlertOctagon className="w-3.5 h-3.5" />
            The Unlikely Hero's Dilemma
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
            When Everything Fails at 2 AM, Who Coordinates the Chaos?
          </h2>
          <p className="text-slate-400 text-base sm:text-lg leading-relaxed">
            Every large university campus, hospital network, or commercial portfolio relies on someone whose entire job is responding when things go wrong.
          </p>
        </div>

        {/* Narrative Card */}
        <div className="glass-panel rounded-2xl p-8 sm:p-10 mb-16 border border-white/10 relative overflow-hidden">
          <div className="max-w-4xl mx-auto space-y-6 text-slate-300 text-base sm:text-lg leading-relaxed">
            <p>
              A water main breaks in Building C at 2 AM. The HVAC controller in the hospital neonatal intensive care unit flags a sudden temperature rise because its chilled water loop was severed. A contracted elevator repair crew no-shows for the third time this quarter. Meanwhile, a State Fire Marshal arrives tomorrow morning for an unannounced inspection that nobody assembled documentation for.
            </p>
            <p>
              That person coordinates all of this with midnight phone calls, fragmented spreadsheets, and decades of unwritten tribal knowledge locked inside their head. When they retire, that critical wisdom ("Building F electrical panel trips in high humidity," "Vendor A is always late during winter storms") walks out the door forever.
            </p>
            <p className="text-amber-300/90 font-medium">
              ARCHON was purpose-built to empower this Operations Director with an autonomous, governed AI fleet that acts instantly, coordinates seamlessly, and never forgets.
            </p>
          </div>
        </div>

        {/* 3 Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((s, idx) => {
            const Icon = s.icon;
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="glass-panel rounded-xl p-6 border border-white/10 text-center space-y-3"
              >
                <div className="mx-auto w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Icon className="w-6 h-6" />
                </div>
                <div className="text-3xl sm:text-4xl font-extrabold text-white font-mono">
                  {s.stat}
                </div>
                <p className="text-sm text-slate-300 font-medium leading-snug">
                  {s.label}
                </p>
                <div className="text-[11px] text-slate-500 pt-2 border-t border-white/5">
                  Source: {s.source}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
