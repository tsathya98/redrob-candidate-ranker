import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ChevronRight, TrendingUp, Sparkles, AlertOctagon } from "lucide-react";
import type { RankedRow, HoneypotRow } from "@/lib/api";
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

function Toggle({ mode, set }: { mode: "smart" | "keyword"; set: (m: "smart" | "keyword") => void }) {
  return (
    <div className="flex rounded-xl border border-white/10 bg-white/5 p-0.5 text-xs">
      {(["smart", "keyword"] as const).map((m) => (
        <button key={m} onClick={() => set(m)}
          className={cn("rounded-lg px-2.5 py-1 font-medium transition-colors",
            mode === m ? "bg-violet-500/30 text-white" : "text-[#8b90a8] hover:text-white")}>
          {m === "smart" ? "Smart" : "Keyword (ATS)"}
        </button>
      ))}
    </div>
  );
}

export function Leaderboard({
  rows, honeypots, selectedId, onSelect, onHoneypot,
}: {
  rows: RankedRow[]; honeypots: HoneypotRow[]; selectedId: string | null;
  onSelect: (id: string) => void; onHoneypot: (id: string) => void;
}) {
  const [mode, setMode] = useState<"smart" | "keyword">(
    () => (typeof location !== "undefined"
      && new URLSearchParams(location.search).get("view") === "keyword" ? "keyword" : "smart"),
  );
  const smartRank = useMemo(() => new Map(rows.map((r) => [r.candidate_id, r.rank])), [rows]);
  // keyword (ATS) view: everyone (incl. honeypots) sorted by raw keyword count
  const naive = useMemo(
    () => [...rows, ...honeypots].sort((a, b) => b.naive_score - a.naive_score),
    [rows, honeypots],
  );

  return (
    <Card className="flex h-full flex-col p-5">
      <div className="mb-3 flex items-center justify-between gap-2">
        <SectionTitle kicker="Ranked Output"
          title={mode === "smart" ? `Top candidates (${rows.length})` : "What a keyword ranker would pick"}
          icon={<TrendingUp className="h-5 w-5 text-cyan-300" />} />
        <Toggle mode={mode} set={setMode} />
      </div>

      {mode === "keyword" && (
        <div className="mb-2 flex items-center gap-1.5 rounded-lg bg-amber-400/[0.07] px-2.5 py-1.5 text-[11px] text-amber-200/90">
          <Sparkles className="h-3.5 w-3.5" /> Sorted by raw skill-keyword count — honeypots &amp; stuffers float to the top; our engine sinks or excludes them.
        </div>
      )}

      <div className="-mr-2 space-y-1.5 overflow-y-auto pr-2">
        {mode === "smart" && rows.map((r, i) => (
          <motion.button key={r.candidate_id}
            initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i * 0.015, 0.5) }}
            onClick={() => onSelect(r.candidate_id)}
            className={cn("group flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left transition-all",
              selectedId === r.candidate_id ? "border-violet-400/40 bg-violet-400/[0.08]"
                : "border-transparent hover:border-white/10 hover:bg-white/[0.03]")}>
            <span className="w-7 shrink-0 text-center text-sm font-semibold tabular-nums text-[#6f7596]">{r.rank}</span>
            <ScoreRing score={r.score} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="truncate text-sm font-medium text-white">{r.title}</span>
                {r.rank <= 10 && <Badge tone="good">top&nbsp;10</Badge>}
              </div>
              <div className="truncate text-xs text-[#8b90a8]">{r.yoe.toFixed(1)}y · {r.company} · {r.location}</div>
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

        {mode === "keyword" && naive.map((r, i) => {
          const isHp = r.status === "honeypot_filtered";
          const sRank = smartRank.get(r.candidate_id);
          return (
            <motion.button key={r.candidate_id}
              initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i * 0.015, 0.5) }}
              onClick={() => (isHp ? onHoneypot(r.candidate_id) : onSelect(r.candidate_id))}
              className={cn("group flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left transition-all",
                isHp ? "border-rose-400/30 bg-rose-400/[0.06] hover:bg-rose-400/[0.1]"
                  : "border-transparent hover:border-white/10 hover:bg-white/[0.03]")}>
              <span className="w-7 shrink-0 text-center text-sm font-semibold tabular-nums text-[#6f7596]">{i + 1}</span>
              <div className="grid h-11 w-11 shrink-0 place-items-center rounded-full border border-white/10 text-[11px] font-semibold tabular-nums text-[#aeb4cf]">
                {r.naive_score}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="truncate text-sm font-medium text-white">{r.title}</span>
                  {isHp
                    ? <Badge tone="bad"><AlertOctagon className="h-3 w-3" /> honeypot</Badge>
                    : sRank && sRank <= 10
                      ? <Badge tone="good">our&nbsp;#{sRank}</Badge>
                      : <Badge tone="warn">our&nbsp;#{sRank ?? "100+"}</Badge>}
                </div>
                <div className="truncate text-xs text-[#8b90a8]">
                  {r.yoe.toFixed(1)}y · {r.company} · {r.location}
                </div>
                <div className="mt-0.5 text-[11px] text-[#6f7596]">{r.naive_score} matching skill keywords</div>
              </div>
              <ChevronRight className="h-4 w-4 shrink-0 text-[#454a66] group-hover:text-white" />
            </motion.button>
          );
        })}
      </div>
    </Card>
  );
}
