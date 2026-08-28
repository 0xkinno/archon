"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Building2, Layers, Users, ShieldAlert, Activity, RefreshCw } from "lucide-react";

export default function CampusPage() {
  const [buildings, setBuildings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchBuildings = async () => {
    setLoading(true);
    try {
      const data = await api.getBuildings();
      setBuildings(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBuildings();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Campus Topology & Facilities
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Spatial interdependencies, chilled water loops, and electrical substations across 12 buildings
          </p>
        </div>

        <button
          onClick={fetchBuildings}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {buildings.map((b) => (
          <div key={b.building_id} className="glass-panel-interactive rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                {b.building_id}
              </span>
              <span className="text-xs font-mono text-slate-400">
                {b.floors} Floors
              </span>
            </div>

            <div>
              <h3 className="text-base font-bold text-white mb-1">{b.name}</h3>
              <div className="text-xs text-slate-400 font-mono">{b.address}</div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed bg-navy-950/70 p-3 rounded-lg border border-white/5">
              {b.special_requirements}
            </p>

            <div className="space-y-2 pt-2 border-t border-white/5 text-xs font-mono">
              <div className="flex items-center justify-between text-slate-400">
                <span>Occupancy Capacity:</span>
                <span className="text-white font-bold">{b.occupancy_capacity} people</span>
              </div>

              {b.critical_zones && b.critical_zones.length > 0 && (
                <div className="pt-1">
                  <span className="text-[10px] text-red-400 uppercase tracking-wider block mb-1">
                    Critical Zones:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {b.critical_zones.map((cz: string) => (
                      <span key={cz} className="text-[10px] px-2 py-0.5 rounded bg-red-500/10 text-red-300 border border-red-500/20">
                        {cz}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
