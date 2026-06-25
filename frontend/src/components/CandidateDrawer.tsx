import { motion, AnimatePresence } from "framer-motion";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer,
} from "recharts";
import {
  Quote, AlertTriangle, ShieldAlert, Sparkles, Loader2, Building2, GraduationCap,
} from "lucide-react";
import { useCandidate, useExplain } from "@/lib/hooks";
import { scoreColor } from "@/lib/utils";
import { Card, Badge, SectionTitle, Meter } from "./ui";

const COMP_LABEL: Record<string, string> = {
  relevance: "Relevance", title_career: "Title/Career", experience: "Experience",
  skill_depth: "Skill depth", education: "Education",
};

export function CandidateDrawer({ id }: { id: string | null }) {
  const { data: d, isLoading } = useCandidate(id);
  const explain = useExplain();

  if (!id) {
    return (
      <Card className="grid h-full place-items-center p-6 text-center">
        <div className="text-sm text-[#6f7596]">
          <Sparkles className="mx-auto mb-2 h-6 w-6 text-violet-300/60" />
          Select a candidate to see the score breakdown,<br />evidence, and gap analysis.
        </div>
      </Card>
    );
  }
  if (isLoading || !d) return <Card className="h-full animate-pulse p-5" />;

  const radar = Object.entries(d.components).map(([k, v]) => ({ axis: COMP_LABEL[k] ?? k, v }));

  return (
    <Card className="flex h-full flex-col overflow-hidden p-5">
      <div className="-mr-2 overflow-y-auto pr-2">
        {/* header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-white">{d.title}</h2>
            <div className="mt-0.5 text-xs text-[#8b90a8]">
              {d.name} · {d.yoe.toFixed(1)}y · {d.company} · {d.location}
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold tabular-nums" style={{ color: scoreColor(d.score) }}>
              {(d.score * 100).toFixed(0)}
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[#6f7596]">score</div>
          </div>
        </div>

        {d.is_honeypot && (
          <div className="mt-3 flex items-center gap-2 rounded-xl border border-rose-400/30 bg-rose-400/10 p-2.5 text-xs text-rose-200">
            <ShieldAlert className="h-4 w-4 shrink-0" />
            <span>Honeypot — impossible profile ({d.honeypot_flags.join(", ")}). Forced out of ranking.</span>
          </div>
        )}

        {/* radar */}
        <div className="mt-4 h-48">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radar} outerRadius="72%">
              <PolarGrid stroke="#ffffff14" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: "#8b90a8", fontSize: 10 }} />
              <Radar dataKey="v" stroke="#7c5cff" fill="#7c5cff" fillOpacity={0.35}
                     isAnimationActive={false} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-between text-[11px] text-[#6f7596]">
          <span>availability ×{d.modifier.toFixed(2)}</span>
          {d.penalties.length > 0 && <span className="text-rose-300">{d.penalties.length} penalty applied</span>}
        </div>

        {/* Slice-2 relevance signals: lexical + semantic + cross-encoder rerank */}
        {d.relevance_parts && Object.keys(d.relevance_parts).length > 0 && (
          <div className="mt-3 rounded-xl bg-white/[0.03] p-3">
            <div className="mb-2 flex items-center justify-between text-[11px] uppercase tracking-wider text-[#6f7596]">
              <span>Relevance signals</span>
              {d.reranked && <Badge tone="accent">cross-encoder reranked</Badge>}
            </div>
            <div className="space-y-2">
              {([["lexical", "Lexical (keywords)", "#22d3ee"],
                 ["semantic", "Semantic (embeddings)", "#7c5cff"],
                 ["rerank", "Cross-encoder (bge-reranker)", "#34d399"]] as const).map(([k, label, color]) => {
                const v = d.relevance_parts[k];
                if (v === undefined) return null;
                return (
                  <div key={k}>
                    <div className="mb-1 flex justify-between text-[11px]">
                      <span className="text-[#cdd2e8]">{label}</span>
                      <span className="tabular-nums text-[#6f7596]">{(v * 100).toFixed(0)}</span>
                    </div>
                    <Meter value={v} color={color} />
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* reasoning */}
        <div className="mt-4 rounded-xl bg-white/[0.03] p-3">
          <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-[#6f7596]">
            <Quote className="h-3 w-3" /> Why this rank
          </div>
          <p className="mt-1 text-sm text-[#dfe3f3]">{d.reasoning}</p>
        </div>

        {/* reading between the lines */}
        {d.reading_between_lines.length > 0 && (
          <div className="mt-4">
            <SectionTitle kicker="Contextual Relevance" title="Reading between the lines" />
            <div className="space-y-2">
              {d.reading_between_lines.slice(0, 4).map((r) => (
                <div key={r.concept} className="rounded-lg border border-white/5 bg-white/[0.02] p-2.5">
                  <Badge tone="accent">{r.concept}</Badge>
                  {r.snippets.slice(0, 1).map((s, i) => (
                    <p key={i} className="mt-1.5 text-xs italic text-[#aeb4cf]">{s}</p>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* gaps + concerns */}
        {(d.gaps.length > 0 || d.concerns.length > 0) && (
          <div className="mt-4 grid grid-cols-1 gap-2">
            {d.gaps.length > 0 && (
              <div className="rounded-lg border border-amber-400/20 bg-amber-400/[0.06] p-2.5">
                <div className="mb-1 flex items-center gap-1.5 text-xs font-medium text-amber-300">
                  <AlertTriangle className="h-3.5 w-3.5" /> Gap analysis (missing must-haves)
                </div>
                <div className="flex flex-wrap gap-1">
                  {d.gaps.map((g) => <Badge key={g} tone="warn">{g}</Badge>)}
                </div>
              </div>
            )}
            {d.concerns.length > 0 && (
              <div className="text-xs text-[#8b90a8]">
                <span className="font-medium text-[#aeb4cf]">Honest concerns: </span>
                {d.concerns.join("; ")}.
              </div>
            )}
          </div>
        )}

        {/* career history */}
        <div className="mt-4">
          <SectionTitle title="Career" icon={<Building2 className="h-4 w-4 text-[#8b90a8]" />} />
          <div className="space-y-1.5">
            {d.career_history.slice(0, 3).map((j, i) => (
              <div key={i} className="rounded-lg bg-white/[0.02] p-2 text-xs">
                <div className="font-medium text-[#dfe3f3]">{j.title} · {j.company}</div>
                <p className="mt-0.5 line-clamp-2 text-[#8b90a8]">{j.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* education */}
        {d.education.length > 0 && (
          <div className="mt-3 flex items-center gap-2 text-xs text-[#8b90a8]">
            <GraduationCap className="h-4 w-4" />
            {d.education[0].degree} {d.education[0].field_of_study} · {d.education[0].institution}
          </div>
        )}

        {/* optional LLM narration */}
        <div className="mt-4 border-t border-white/5 pt-3">
          <button
            onClick={() => explain.mutate(id)}
            disabled={explain.isPending}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-violet-400/30 bg-violet-400/10 px-3 py-2 text-sm font-medium text-violet-200 transition hover:bg-violet-400/20 disabled:opacity-60"
          >
            {explain.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            Narrate with AI <span className="text-[10px] text-violet-300/70">(optional · demo-only)</span>
          </button>
          <AnimatePresence>
            {explain.isError && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="mt-2 text-xs text-[#6f7596]">
                LLM narration is off (no API key). The ranking itself is fully offline — this panel is just a flourish.
              </motion.p>
            )}
            {explain.data && (
              <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
                className="mt-2 rounded-xl bg-white/[0.03] p-3 text-sm text-[#dfe3f3]">
                {explain.data.explanation}
                <div className="mt-1 text-[10px] text-[#6f7596]">generated by {explain.data.model} · does not affect ranking</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </Card>
  );
}
