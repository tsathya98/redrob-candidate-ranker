import { motion } from "framer-motion";
import { Target, CheckCircle2, PlusCircle, XCircle } from "lucide-react";
import { useJd } from "@/lib/hooks";
import { Card, Badge, SectionTitle, Meter } from "./ui";

export function JdIntelligence() {
  const { data: jd } = useJd();
  if (!jd) return <Card className="h-full animate-pulse p-5" />;

  return (
    <Card className="flex h-full flex-col p-5">
      <SectionTitle kicker="Deep Job Understanding" title="JD Intelligence"
        icon={<Target className="h-5 w-5 text-violet-300" />} />
      <div className="mb-4 rounded-xl bg-white/[0.03] p-3 text-sm">
        <div className="font-medium text-white">{jd.title}</div>
        <div className="mt-1 text-xs text-[#8b90a8]">{jd.experience_band} · {jd.location}</div>
      </div>

      <div className="space-y-4 overflow-y-auto pr-1">
        <div>
          <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-300">
            <CheckCircle2 className="h-3.5 w-3.5" /> Must-have (gates)
          </div>
          <div className="space-y-2">
            {jd.must_have.map((m, i) => (
              <motion.div key={m.name} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}>
                <div className="mb-1 flex justify-between text-xs">
                  <span className="text-[#cdd2e8]">{m.name}</span>
                  <span className="tabular-nums text-[#6f7596]">{m.weight.toFixed(1)}</span>
                </div>
                <Meter value={m.weight} color="#34d399" />
              </motion.div>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-violet-300">
            <PlusCircle className="h-3.5 w-3.5" /> Nice-to-have
          </div>
          <div className="flex flex-wrap gap-1.5">
            {jd.nice_to_have.map((m) => <Badge key={m.name} tone="accent">{m.name}</Badge>)}
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-rose-300">
            <XCircle className="h-3.5 w-3.5" /> Down-weighted (do NOT want)
          </div>
          <div className="space-y-1.5">
            {jd.negative.map((m) => (
              <div key={m.name} className="flex items-center justify-between rounded-lg bg-rose-400/[0.06] px-2.5 py-1.5 text-xs">
                <span className="text-[#cdd2e8]">{m.name}</span>
                {m.penalty && <Badge tone="bad">{m.penalty}</Badge>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
