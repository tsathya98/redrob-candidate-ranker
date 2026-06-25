import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, children }: { className?: string; children?: ReactNode }) {
  return <div className={cn("glass rounded-2xl", className)}>{children}</div>;
}

export function Badge({
  children, tone = "default", className,
}: { children: ReactNode; tone?: "default" | "good" | "warn" | "bad" | "accent"; className?: string }) {
  const tones: Record<string, string> = {
    default: "bg-white/5 text-[#aeb4cf] border-white/10",
    good: "bg-emerald-400/10 text-emerald-300 border-emerald-400/20",
    warn: "bg-amber-400/10 text-amber-300 border-amber-400/20",
    bad: "bg-rose-400/10 text-rose-300 border-rose-400/20",
    accent: "bg-violet-400/10 text-violet-300 border-violet-400/20",
  };
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium",
      tones[tone], className)}>
      {children}
    </span>
  );
}

export function SectionTitle({ kicker, title, icon }: { kicker?: string; title: string; icon?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center gap-2">
      {icon}
      <div>
        {kicker && <div className="text-[11px] uppercase tracking-widest text-[#6f7596]">{kicker}</div>}
        <h2 className="text-base font-semibold text-white">{title}</h2>
      </div>
    </div>
  );
}

export function Meter({ value, color }: { value: number; color: string }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
      <div className="h-full rounded-full transition-all"
        style={{ width: `${Math.max(2, Math.min(100, value * 100))}%`, background: color }} />
    </div>
  );
}
