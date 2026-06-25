import { motion } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { Card } from "./ui";

type Stage = { n: string; label: string; sub: string; tone: keyof typeof TONES };

const TONES = {
  slate: { dot: "#8b90a8", text: "text-[#e7e9f3]" },
  rose: { dot: "#fb7185", text: "text-rose-300" },
  cyan: { dot: "#22d3ee", text: "text-cyan-300" },
  violet: { dot: "#a78bfa", text: "text-violet-300" },
  emerald: { dot: "#34d399", text: "text-emerald-300" },
};

// The real production pipeline (offline precompute -> CPU-only rank). Demo runs an 80-candidate sample.
const STAGES: Stage[] = [
  { n: "100,000", label: "candidate pool", sub: "streamed, JSONL", tone: "slate" },
  { n: "-65", label: "honeypots removed", sub: "impossibility filter", tone: "rose" },
  { n: "4,000", label: "recall pool", sub: "structured score", tone: "cyan" },
  { n: "600", label: "reranked shortlist", sub: "bge-small + bge-reranker", tone: "violet" },
  { n: "100", label: "final ranked", sub: "CPU · offline · ~150s", tone: "emerald" },
];

export function PipelineFunnel() {
  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-[11px] uppercase tracking-widest text-[#6f7596]">Ranking pipeline</div>
        <div className="text-[11px] text-[#5a5f7d]">offline precompute → CPU-only rank · live demo on an 80-candidate sample</div>
      </div>
      <div className="flex items-stretch gap-1 overflow-x-auto">
        {STAGES.map((s, i) => {
          const t = TONES[s.tone];
          return (
            <div key={s.label} className="flex flex-1 items-center gap-1">
              <motion.div
                initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 * i, type: "spring", stiffness: 220, damping: 22 }}
                className="flex-1 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2.5"
              >
                <div className="flex items-baseline gap-1.5">
                  <span className="inline-block h-1.5 w-1.5 rounded-full" style={{ background: t.dot }} />
                  <span className={`text-lg font-bold tabular-nums ${t.text}`}>{s.n}</span>
                </div>
                <div className="mt-0.5 text-xs font-medium text-[#cdd2e8]">{s.label}</div>
                <div className="text-[10px] text-[#6f7596]">{s.sub}</div>
              </motion.div>
              {i < STAGES.length - 1 && (
                <ChevronRight className="h-4 w-4 shrink-0 text-[#3a3f5a]" />
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
