#!/usr/bin/env python3
"""Compress all 100k candidates into compact records for an independent LLM cross-validation.

Each candidate -> ~120-token line (substance the LLM needs: title, YoE, company/size/industry, career
descriptions, key skills, location, availability). Honeypots are INCLUDED and UNLABELED on purpose, so the
LLM's avoidance of them independently validates our honeypot filter. Writes WINDOW files of N each.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import data_loader

OUT = Path("/home/tsath/.claude/jobs/80528b4c/tmp/llmval")
WIN = 5000

def compact(c: dict) -> str:
    p = c.get("profile", {})
    parts = [f"{c['candidate_id']} | {p.get('current_title','?')} | {p.get('years_of_experience','?')}y "
             f"| {p.get('current_company','?')} ({p.get('current_company_size','?')}, {p.get('current_industry','?')})"]
    ch = []
    for j in c.get("career_history", [])[:3]:
        d = (j.get("description") or "").replace("\n", " ")[:90]
        ch.append(f"{j.get('title','?')}@{j.get('company','?')}[{d}]")
    parts.append("career: " + " ; ".join(ch))
    sk = [f"{s.get('name')}({(s.get('proficiency') or '')[:3]})" for s in c.get("skills", [])][:9]
    parts.append("skills: " + ", ".join(sk))
    s = c.get("redrob_signals", {})
    parts.append(f"{p.get('location','?')}, {p.get('country','?')} | resp={s.get('recruiter_response_rate')} "
                 f"active={s.get('last_active_date')} otw={s.get('open_to_work_flag')} "
                 f"notice={s.get('notice_period_days')}d reloc={s.get('willing_to_relocate')}")
    return " || ".join(parts)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    buf, widx, n = [], 0, 0
    for c in data_loader.iter_candidates("data/candidates.jsonl"):
        buf.append(compact(c)); n += 1
        if len(buf) == WIN:
            (OUT / f"win_{widx:02d}.txt").write_text("\n".join(buf), encoding="utf-8")
            widx += 1; buf = []
    if buf:
        (OUT / f"win_{widx:02d}.txt").write_text("\n".join(buf), encoding="utf-8"); widx += 1
    print(f"wrote {widx} windows, {n} candidates total -> {OUT}")

if __name__ == "__main__":
    main()
