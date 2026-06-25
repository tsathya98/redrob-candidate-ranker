import { motion, AnimatePresence } from "framer-motion";
import { X, ShieldAlert } from "lucide-react";
import { useCandidate } from "@/lib/hooks";

const FLAG_EXPLAIN: Record<string, string> = {
  duration_exceeds_span: "A role's stated duration is longer than the actual time between its start and end dates.",
  experience_exceeds_career_span: "Claimed total years of experience exceed the entire career timeline.",
  expert_skill_zero_duration: "Rated 'expert'/'advanced' in a skill used for 0 months.",
  expert_skill_failed_assessment: "Self-rated 'expert' but scored near-zero on the platform assessment.",
  career_dates_reversed: "A role's start date is after its end date.",
  current_role_has_end_date: "Marked as the current role yet has an end date.",
  education_years_reversed: "Education start year is after its end year.",
  education_span_implausible: "Education spans an implausibly long number of years.",
};

function spanYears(ch: { start_date: string; end_date: string | null }[]): number {
  const starts = ch.map((j) => +new Date(j.start_date)).filter((n) => !isNaN(n));
  const ends = ch.map((j) => (j.end_date ? +new Date(j.end_date) : Date.now())).filter((n) => !isNaN(n));
  if (!starts.length) return 0;
  return Math.max(0, (Math.max(...ends) - Math.min(...starts)) / (365.25 * 864e5));
}

export function HoneypotModal({ id, onClose }: { id: string | null; onClose: () => void }) {
  const { data: d } = useCandidate(id);
  const expertZero = d?.skills?.filter(
    (s) => ["expert", "advanced"].includes(s.proficiency) && s.duration_months === 0,
  ) ?? [];
  const span = d ? spanYears(d.career_history) : 0;

  return (
    <AnimatePresence>
      {id && (
        <motion.div
          className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur-sm"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}
        >
          <motion.div
            onClick={(e) => e.stopPropagation()}
            initial={{ scale: 0.95, opacity: 0, y: 10 }} animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.97, opacity: 0 }} transition={{ type: "spring", stiffness: 260, damping: 24 }}
            className="w-full max-w-lg rounded-2xl border border-rose-400/25 bg-[#0d0f17] p-6 shadow-2xl"
          >
            <div className="mb-4 flex items-start justify-between gap-3">
              <div className="flex items-center gap-2 text-rose-300">
                <ShieldAlert className="h-5 w-5" />
                <div>
                  <div className="text-[11px] uppercase tracking-widest text-rose-300/70">Honeypot — excluded</div>
                  <div className="text-base font-semibold text-white">{d?.title ?? "…"}</div>
                </div>
              </div>
              <button onClick={onClose} className="rounded-lg p-1 text-[#8b90a8] hover:bg-white/10 hover:text-white">
                <X className="h-5 w-5" />
              </button>
            </div>

            {d && (
              <div className="text-xs text-[#8b90a8]">
                {d.name} · {d.company} · {d.location}
              </div>
            )}

            <div className="mt-4 space-y-2">
              <div className="text-[11px] uppercase tracking-widest text-[#6f7596]">Why it is impossible</div>
              {(d?.honeypot_flags ?? []).map((f) => (
                <div key={f} className="rounded-xl border border-rose-400/15 bg-rose-400/[0.06] p-3">
                  <div className="font-mono text-[11px] text-rose-300/90">{f}</div>
                  <div className="mt-0.5 text-sm text-[#cdd2e8]">{FLAG_EXPLAIN[f] ?? "Internal inconsistency in the profile."}</div>
                </div>
              ))}
            </div>

            {d && (
              <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                <div className="rounded-xl bg-white/[0.04] p-3">
                  <div className="text-[11px] text-[#6f7596]">Claimed experience</div>
                  <div className="font-semibold text-white">{d.yoe.toFixed(1)} yrs</div>
                </div>
                <div className="rounded-xl bg-white/[0.04] p-3">
                  <div className="text-[11px] text-[#6f7596]">Actual career span</div>
                  <div className="font-semibold text-white">{span.toFixed(1)} yrs</div>
                </div>
              </div>
            )}

            {expertZero.length > 0 && (
              <div className="mt-3 rounded-xl bg-white/[0.04] p-3 text-sm">
                <div className="text-[11px] text-[#6f7596]">"Expert" skills used 0 months</div>
                <div className="mt-1 text-[#cdd2e8]">{expertZero.map((s) => s.name).join(", ")}</div>
              </div>
            )}

            <div className="mt-4 text-[11px] text-[#5a5f7d]">
              Detected by deterministic impossibility checks (no keywords) — forced to the bottom before ranking.
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
