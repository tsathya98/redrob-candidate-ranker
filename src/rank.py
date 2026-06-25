#!/usr/bin/env python3
"""CLI entry point — the single reproduce command (docs/04 Section 10.3).

    python src/rank.py --candidates data/candidates.jsonl --out submission.csv

Pipeline (docs/05): stream pool -> honeypot filter -> score -> keep top-K -> rank top-100 -> reason -> CSV.
Runs CPU-only, no network. Slice 1 is rules+lexical (no embeddings); embeddings blend in at Slice 2.
"""

from __future__ import annotations

import argparse
import csv
import heapq
import sys
import time
from pathlib import Path

# Support running both as a module (python -m src.rank) and as a script (python src/rank.py).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src import data_loader, honeypot, reasoning, scoring
else:
    from . import data_loader, honeypot, reasoning, scoring

REQUIRED_HEADER = ["candidate_id", "rank", "score", "reasoning"]
TOP_K_BUFFER = 1000  # keep this many best-scored candidates in memory (top-100 is safely within)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rank.py",
        description="Rank the top-100 best-fit candidates for the Redrob Senior AI Engineer JD.",
    )
    p.add_argument("--candidates", required=True, type=Path, help="Path to candidates.jsonl (or .jsonl.gz).")
    p.add_argument("--out", required=True, type=Path, help="Output CSV (candidate_id,rank,score,reasoning).")
    p.add_argument("--embeddings", type=Path, default=None, help="Precomputed embeddings artifact (Slice 2).")
    p.add_argument("--top-n", type=int, default=100, help="Number of candidates to output (challenge: 100).")
    p.add_argument("--quiet", action="store_true", help="Suppress progress output.")
    return p.parse_args(argv)


def write_submission(rows: list[dict], out_path: Path) -> None:
    """Write ranked rows to a spec-compliant CSV (header + exactly top-n data rows)."""
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REQUIRED_HEADER)
        w.writeheader()
        for r in rows:
            w.writerow({
                "candidate_id": r["candidate_id"],
                "rank": r["rank"],
                "score": f"{r['score']:.6f}",
                "reasoning": r["reasoning"],
            })


def run(args: argparse.Namespace) -> list[dict]:
    """Execute the ranking pipeline and return the ranked top-n rows."""
    t0 = time.time()
    heap: list[tuple] = []          # min-heap of (score, candidate_id, counter)
    payloads: dict[int, tuple] = {} # counter -> (scored, candidate)
    counter = 0
    n_total = n_honeypot = 0

    for cand in data_loader.iter_candidates(args.candidates):
        n_total += 1
        if honeypot.is_honeypot(cand):       # force impossible profiles out of contention (DQ safety)
            n_honeypot += 1
            continue
        scored = scoring.score_candidate(cand)
        key = (scored["score"], scored["candidate_id"], counter)
        if len(heap) < TOP_K_BUFFER:
            heapq.heappush(heap, key)
            payloads[counter] = (scored, cand)
        elif key > heap[0]:
            _, _, evicted = heapq.heappushpop(heap, key)
            payloads.pop(evicted, None)
            payloads[counter] = (scored, cand)
        counter += 1
        if not args.quiet and n_total % 20000 == 0:
            print(f"  ...scored {n_total:,} ({n_honeypot} honeypots filtered)", file=sys.stderr)

    scored_list = [payloads[c][0] for (_, _, c) in heap]
    top = scoring.rank_pool(scored_list, top_n=args.top_n)

    cand_by_id = {payloads[c][1]["candidate_id"]: payloads[c][1] for (_, _, c) in heap}
    rows = []
    for s in top:
        cand = cand_by_id[s["candidate_id"]]
        rows.append({
            "candidate_id": s["candidate_id"],
            "rank": s["rank"],
            "score": s["score"],
            "reasoning": reasoning.build_reasoning(cand, s, s["rank"]),
        })

    if not args.quiet:
        dt = time.time() - t0
        print(f"Scored {n_total:,} candidates ({n_honeypot} honeypots filtered) in {dt:.1f}s; "
              f"top score {rows[0]['score']:.4f}, cutoff {rows[-1]['score']:.4f}", file=sys.stderr)
    return rows


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows = run(args)
    write_submission(rows, args.out)
    print(f"Wrote {len(rows)} ranked candidates to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
