#!/usr/bin/env python3
"""Print the key profile facts for given candidate IDs (manual top-N audit helper).

The manual audit is our best relevance proxy in the absence of a ground truth: read the actual
profiles behind the top ranks and check they are genuine fits (not stuffers / honeypots / juniors).

Usage:
  uv run python scripts/audit_candidates.py CAND_xxxxxxx CAND_xxxxxxx ...
  # audit the current top-10:
  awk -F, 'NR>1 && NR<=11 {print $1}' submission.csv | xargs uv run python scripts/audit_candidates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import data_loader  # noqa: E402


def show(c: dict) -> None:
    p = c["profile"]
    s = c.get("redrob_signals", {})
    print(f"### {c['candidate_id']} | {p.get('current_title')} @ {p.get('current_company')} | "
          f"{p.get('years_of_experience')}y | {p.get('location')}, {p.get('country')}")
    print(f"    headline: {p.get('headline', '')[:110]}")
    for j in c.get("career_history", [])[:4]:
        d = (j.get("description") or "")[:160]
        print(f"    • {j.get('title')} @ {j.get('company')} "
              f"({j.get('duration_months')}mo, {j.get('company_size')}): {d}")
    sk = [f"{x.get('name')}({x.get('proficiency', '')[:3]})" for x in c.get("skills", [])][:12]
    print(f"    skills: {', '.join(sk)}")
    print(f"    signals: resp={s.get('recruiter_response_rate')} active={s.get('last_active_date')} "
          f"otw={s.get('open_to_work_flag')} notice={s.get('notice_period_days')} "
          f"reloc={s.get('willing_to_relocate')}\n")


def main(argv: list[str]) -> int:
    want = set(argv)
    if not want:
        print("usage: audit_candidates.py CAND_xxx [CAND_yyy ...]", file=sys.stderr)
        return 2
    found = {}
    for c in data_loader.iter_candidates("data/candidates.jsonl"):
        if c["candidate_id"] in want:
            found[c["candidate_id"]] = c
            if len(found) == len(want):
                break
    for cid in argv:
        if cid in found:
            show(found[cid])
        else:
            print(f"### {cid} NOT FOUND\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
