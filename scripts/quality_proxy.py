#!/usr/bin/env python3
"""Quality proxy for a submission CSV (no ground truth needed).

The challenge ground truth is hidden, so we cannot compute the real NDCG/MAP before submitting. This
script reports interpretable *proxies* over the top-10/50/100 of a submission so we can compare design
choices (query formulations, weight changes) by their effect on visible quality:

  in-band       fraction with 5-9 years of experience (the JD band)
  senior-title  fraction whose current title is senior/staff/lead/principal
  juniors       fraction whose title is junior/associate/specialist (should be ~0 near the top)
  ranking-work  fraction whose career descriptions show ranking/retrieval/recsys/search work
  available     fraction with recruiter_response_rate >= 0.5
  medYoE        median years of experience

Usage:
  uv run python scripts/quality_proxy.py submission.csv [other_submission.csv ...]
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import data_loader  # noqa: E402

SENIOR = ("senior", "staff", "lead", "principal")
JUNIOR = ("junior", "associate", "intern", "specialist")
RANK_DESC = ("ranking", "retrieval", "recommend", "semantic search", "search", "embedding",
             "learning to rank", "relevance")


def _q(c: dict) -> tuple:
    p = c["profile"]
    yoe = p.get("years_of_experience") or 0
    title = (p.get("current_title") or "").lower()
    desc = " ".join((j.get("description") or "") for j in c.get("career_history", [])).lower() + title
    s = c.get("redrob_signals", {})
    return (5 <= yoe <= 9, any(x in title for x in SENIOR), any(x in title for x in JUNIOR),
            any(k in desc for k in RANK_DESC), (s.get("recruiter_response_rate") or 0) >= 0.5)


def main(argv: list[str]) -> int:
    files = argv or ["submission.csv"]
    ids = {fn: [(r["candidate_id"], int(r["rank"])) for r in csv.DictReader(open(fn))] for fn in files}
    allids = {c for lst in ids.values() for c, _ in lst}
    prof = {}
    for c in data_loader.iter_candidates("data/candidates.jsonl"):
        if c["candidate_id"] in allids:
            prof[c["candidate_id"]] = c
        if len(prof) == len(allids):
            break
    for fn, lst in ids.items():
        print(f"=== {Path(fn).name} ===")
        for topn in (10, 50, 100):
            sub = [c for c, r in lst if r <= topn and c in prof]
            rows = [_q(prof[c]) for c in sub]
            n = len(rows) or 1
            yoes = [prof[c]["profile"].get("years_of_experience") or 0 for c in sub]
            print(f"  top-{topn}: in-band {sum(r[0] for r in rows)}/{n}  "
                  f"senior {sum(r[1] for r in rows)}/{n}  juniors {sum(r[2] for r in rows)}/{n}  "
                  f"ranking-work {sum(r[3] for r in rows)}/{n}  available {sum(r[4] for r in rows)}/{n}  "
                  f"medYoE {statistics.median(yoes):.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
