import { motion } from "framer-motion";
import { ChevronRight, TrendingUp } from "lucide-react";
import type { RankedRow } from "@/lib/api";
import { cn, scoreColor } from "@/lib/utils";
import { Card, Badge, SectionTitle } from "./ui";

function ScoreRing({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(1, score));
  const color = scoreColor(score);
  return (
    <div className="relative grid h-11 w-11 place-items-center">
      <svg className="h-11 w-11 -rotate-90" viewBox="0 0 44 44">
        <circle cx="22" cy="22" r="18" fill="none" stroke="#ffffff12" strokeWidth="4" />
        <circle cx="22" cy="22" r="18" fill="none" stroke={color} strokeWidth="4" strokeLinecap="round"
          strokeDasharray={`${pct * 113} 113`} />
      </svg>
      <span className="absolute text-[11px] font-semibold tabular-nums text-white">
        {(score * 100).toFixed(0)}
      </span>
    </div>
  );
}

export function Leaderboard({
  rows, selectedId, onSelect,
}: { rows: RankedRow[]; selectedId: string | null; onSelect: (id: string) => void }) {
  return (
    <Card className="flex h-full flex-col p-5">
      <SectionTitle kicker="Ranked Output" title={`Top candidates (${rows.length})`}
        icon={<TrendingUp className="h-5 w-5 text-cyan-300" />} />
      <div className="-mr-2 space-y-1.5 overflow-y-auto pr-2">
        {rows.map((r, i) => (
          <motion.button
            key={r.candidate_id}
            initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(i * 0.015, 0.5) }}
            onClick={() => onSelect(r.candidate_id)}
            className={cn(
              "group flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left transition-all",
              selectedId === r.candidate_id
                ? "border-violet-400/40 bg-violet-400/[0.08]"
                : "border-transparent hover:border-white/10 hover:bg-white/[0.03]",
            )}
          >
            <span className="w-7 shrink-0 text-center text-sm font-semibold tabular-nums text-[#6f7596]">
              {r.rank}
            </span>
            <ScoreRing score={r.score} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="truncate text-sm font-medium text-white">{r.title}</span>
                {r.rank <= 10 && <Badge tone="good">top&nbsp;10</Badge>}
              </div>
              <div className="truncate text-xs text-[#8b90a8]">
                {r.yoe.toFixed(1)}y · {r.company} · {r.location}
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {r.matched_concepts.slice(0, 3).map((c) => (
                  <span key={c} className="rounded bg-white/5 px-1.5 py-0.5 text-[10px] text-[#aeb4cf]">{c}</span>
                ))}
                {r.concerns.length > 0 && <Badge tone="warn">{r.concerns.length} concern{r.concerns.length > 1 ? "s" : ""}</Badge>}
              </div>
            </div>
            <ChevronRight className="h-4 w-4 shrink-0 text-[#454a66] group-hover:text-white" />
          </motion.button>
        ))}
      </div>
    </Card>
  );
}
