import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Code2, ShieldAlert } from "lucide-react";
import { useRanking, useHealth } from "@/lib/hooks";
import { StatStrip } from "./components/StatStrip";
import { JdIntelligence } from "./components/JdIntelligence";
import { Leaderboard } from "./components/Leaderboard";
import { CandidateDrawer } from "./components/CandidateDrawer";
import { Card, Badge } from "./components/ui";

export default function App() {
  const { data: ranking, isLoading, isError } = useRanking();
  const { data: health } = useHealth();
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    if (ranking && !selected) setSelected(ranking.results[0]?.candidate_id ?? null);
  }, [ranking, selected]);

  return (
    <div className="mx-auto min-h-screen max-w-[1500px] px-4 py-6 lg:px-8">
      {/* header */}
      <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-violet-500/30 to-cyan-400/20 ring-1 ring-white/10">
            <BrainCircuit className="h-6 w-6 text-violet-200" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              <span className="gradient-text">Redrob</span> Intelligent Candidate Discovery
            </h1>
            <p className="text-xs text-[#8b90a8]">
              Hybrid, explainable ranking — substance over keywords · CPU-only · offline
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone={health?.llm_enabled ? "good" : "default"}>
            {health?.llm_enabled ? "LLM narration on" : "100% offline ranking"}
          </Badge>
          <a href="https://github.com/tsathya98/redrob-candidate-ranker" target="_blank"
            className="flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-[#cdd2e8] hover:bg-white/10">
            <Code2 className="h-3.5 w-3.5" /> Repo
          </a>
        </div>
      </header>

      {isError && (
        <Card className="p-6 text-center text-sm text-rose-300">
          Could not reach the ranking API. Start the backend: <code>uvicorn app.main:app --port 8000</code>
        </Card>
      )}

      {ranking && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-5">
          <StatStrip stats={ranking.stats} />
        </motion.div>
      )}

      <div className="grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)_400px]">
        <div className="h-[calc(100vh-240px)] min-h-[520px] max-h-[760px]"><JdIntelligence /></div>
        <div className="h-[calc(100vh-240px)] min-h-[520px] max-h-[760px]">
          {ranking && (
            <Leaderboard rows={ranking.results} selectedId={selected} onSelect={setSelected} />
          )}
          {isLoading && <Card className="h-full animate-pulse" />}
        </div>
        <div className="h-[calc(100vh-240px)] min-h-[520px] max-h-[760px]"><CandidateDrawer id={selected} /></div>
      </div>

      {/* honeypot guardrail strip */}
      {ranking && ranking.honeypots.length > 0 && (
        <Card className="mt-4 p-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-rose-300">
            <ShieldAlert className="h-4 w-4" /> Guardrail — {ranking.honeypots.length} honeypots detected &amp; excluded
          </div>
          <div className="flex flex-wrap gap-2">
            {ranking.honeypots.map((h) => (
              <div key={h.candidate_id} className="rounded-lg border border-rose-400/15 bg-rose-400/[0.05] px-2.5 py-1.5 text-xs">
                <span className="text-[#cdd2e8]">{h.title}</span>
                <span className="ml-2 text-rose-300/80">{h.honeypot_flags[0]}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      <footer className="mt-6 text-center text-[11px] text-[#5a5f7d]">
        Ranking runs CPU-only & offline (≤5 min, no LLM calls). Reasoning is templated from real profile facts.
      </footer>
    </div>
  );
}
