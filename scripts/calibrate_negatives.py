#!/usr/bin/env python3
"""Full-pool calibration of the JD's 'disqualifier' archetypes (docs/09 §3).

Before implementing a penalty for a JD negative, we measure whether it actually manifests in the pool.
This script quantifies the three JD 'disqualifiers we actually apply' so the decision to implement (or
NOT implement) each is evidence-based — the same discipline that made us reject a honeypot check which
fired on ~9% of legitimate profiles.

Usage:
  uv run python scripts/calibrate_negatives.py            # full pool
  uv run python scripts/calibrate_negatives.py 20000      # first N (faster)
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import data_loader  # noqa: E402

RESEARCH_TITLE = ("research scientist", "research engineer", "postdoctoral", "postdoc",
                  "research fellow", "research associate", "phd candidate")
UNIV = ("university", "institute of technology", "iit ", "iisc", "indian institute",
        "research lab", "laboratory", "labs", "academia", "college")
MGMT_TITLE = ("architect", "tech lead", "technical lead", "engineering manager", "vice president",
              " vp", "director", "head of", "principal architect", "staff architect")


def main(argv: list[str]) -> int:
    limit = int(argv[0]) if argv else 0
    n = research_title = research_company = research_phd = mgmt_current = langchain = 0
    src = data_loader.iter_candidates("data/candidates.jsonl")
    if limit:
        src = itertools.islice(src, limit)
    for c in src:
        n += 1
        p = c.get("profile", {})
        cur = (p.get("current_title") or "").lower()
        titles = [cur] + [(j.get("title") or "").lower() for j in c.get("career_history", [])]
        comps = [(j.get("company") or "").lower() for j in c.get("career_history", [])] + \
                [(p.get("current_company") or "").lower()]
        blob = (p.get("summary", "") + " " + p.get("headline", "")).lower()
        if any(any(r in t for r in RESEARCH_TITLE) for t in titles):
            research_title += 1
        if any(any(u in co for u in UNIV) for co in comps):
            research_company += 1
        if any(k in blob for k in ("phd", "ph.d", "doctorate")):
            research_phd += 1
        if any(m in cur for m in MGMT_TITLE):
            mgmt_current += 1
        if "langchain" in blob or any("langchain" in (j.get("description") or "").lower()
                                      for j in c.get("career_history", [])):
            langchain += 1

    def pct(x: int) -> str:
        return f"{x} ({100 * x / n:.2f}%)"

    print(f"pool n = {n}")
    print(f"  research title anywhere      : {pct(research_title)}")
    print(f"  employer is university/lab   : {pct(research_company)}")
    print(f"  PhD/doctorate in summary     : {pct(research_phd)}")
    print(f"  mgmt/architect CURRENT title : {pct(mgmt_current)}")
    print(f"  langchain in prose/descr     : {pct(langchain)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
