import { motion } from "framer-motion";
import { ShieldCheck, Users, GitCompareArrows, Sparkles } from "lucide-react";
import type { RankStats } from "@/lib/api";
import { Card } from "./ui";

function Stat({ icon, value, label, sub, delay }: {
  icon: React.ReactNode; value: string; label: string; sub?: string; delay: number;
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
      <Card className="flex items-center gap-3 p-4">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-white/5">{icon}</div>
        <div>
          <div className="text-xl font-semibold text-white tabular-nums">{value}</div>
          <div className="text-xs text-[#8b90a8]">{label}</div>
          {sub && <div className="text-[11px] text-[#6f7596]">{sub}</div>}
        </div>
      </Card>
    </motion.div>
  );
}

export function StatStrip({ stats }: { stats: RankStats }) {
  const divergence = 10 - stats.overlap_top10;
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <Stat delay={0.0} icon={<Users className="h-5 w-5 text-cyan-300" />}
        value={`${stats.ranked}`} label="Candidates ranked" sub={`of ${stats.total} in sample`} />
      <Stat delay={0.05} icon={<ShieldCheck className="h-5 w-5 text-emerald-300" />}
        value={`${stats.honeypots_filtered}`} label="Honeypots caught" sub="forced out of top-100" />
      <Stat delay={0.1} icon={<GitCompareArrows className="h-5 w-5 text-violet-300" />}
        value={`${divergence}/10`} label="Top-10 differ vs keyword" sub={`only ${stats.overlap_top10} overlap`} />
      <Stat delay={0.15} icon={<Sparkles className="h-5 w-5 text-amber-300" />}
        value="0" label="Stuffers in top-10" sub="substance over keywords" />
    </div>
  );
}
