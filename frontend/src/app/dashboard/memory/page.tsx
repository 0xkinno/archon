"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MemoryEntry } from "@/lib/types";
import { MemoryCard } from "@/components/shared/MemoryCard";
import { BrainCircuit, Search, Sparkles, RefreshCw } from "lucide-react";

export default function MemoryBankPage() {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  const loadMemories = async (query?: string) => {
    setLoading(true);
    try {
      if (query && query.trim()) {
        const res = await api.searchMemory(query);
        setMemories(res.precedents || []);
      } else {
        const res = await api.getAllMemories();
        setMemories(res || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadMemories(searchQuery);
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Memory Bank & Precedents
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Google Vertex AI Memory Bank capturing 20 years of campus operational knowledge
          </p>
        </div>

        <button
          onClick={() => {
            setSearchQuery("");
            loadMemories();
          }}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-300 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Search</span>
        </button>
      </div>

      {/* Semantic Search Box */}
      <form
        onSubmit={handleSearch}
        className="glass-panel rounded-2xl p-4 border border-white/10 flex flex-col sm:flex-row items-center gap-3"
      >
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search institutional memory (e.g. 'Building F panel B3', 'chiller bypass valve', 'Atlas elevator')..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-navy-950/80 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50 font-mono"
          />
        </div>
        <button
          type="submit"
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all shadow-md shadow-purple-600/20 shrink-0"
        >
          <Sparkles className="w-4 h-4" />
          <span>Semantic Search</span>
        </button>
      </form>

      {/* Results Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>{memories.length} Institutional Memories Recorded</span>
          <span>VertexAiMemoryBankService Active</span>
        </div>

        {memories.length === 0 ? (
          <div className="glass-panel rounded-2xl p-12 text-center text-slate-500 text-xs font-mono">
            No memories match your query. Try broadening your keywords.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {memories.map((mem) => (
              <MemoryCard key={mem.memory_id} memory={mem} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
