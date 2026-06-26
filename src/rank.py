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
import json
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
    p.add_argument("--artifacts", type=Path, default=Path("artifacts"),
                   help="Dir with precomputed semantic.json + reranker.json (Slice 2). Optional.")
    p.add_argument("--top-n", type=int, default=100, help="Number of candidates to output (challenge: 100).")
    p.add_argument("--quiet", action="store_true", help="Suppress progress output.")
    p.add_argument("--lexical-only", action="store_true",
                   help="Run the Slice-1 lexical baseline WITHOUT precomputed artifacts. "
                        "This does NOT reproduce the official submission (which needs `just precompute`).")
    return p.parse_args(argv)


def load_context(artifacts_dir: Path, quiet: bool = False, lexical_only: bool = False) -> dict:
    """Load precomputed Slice-2 artifacts.

    The official submission needs these artifacts. If they are absent we REFUSE by default
    (rather than silently produce a different, lexical-only ranking that won't match the
    submitted CSV) — pass --lexical-only to intentionally run the Slice-1 baseline instead.
    """
    sem_path = artifacts_dir / "semantic.json"
    rer_path = artifacts_dir / "reranker.json"
    if not sem_path.exists():
        if lexical_only:
            if not quiet:
                print("Running Slice-1 lexical baseline (--lexical-only); "
                      "this is NOT the official submission ranking.", file=sys.stderr)
            return {}
        print(
            f"\nERROR: precomputed artifacts not found in '{artifacts_dir}/'.\n"
            "  The official top-100 needs the semantic + cross-encoder artifacts. Build them once\n"
            "  (offline) then re-run:\n"
            "      just precompute-install && just precompute && just rank\n"
            "  Or, to run the lexical-only baseline (DIFFERENT ranking), pass: --lexical-only\n",
            file=sys.stderr,
        )
        raise SystemExit(2)
    ctx: dict = {"semantic": json.loads(sem_path.read_text())}
    if rer_path.exists():
        rer = json.loads(rer_path.read_text())
        ctx["reranker"] = rer
        vals = list(rer.values())
        ctx["rerank_range"] = (min(vals), max(vals)) if vals else (0.0, 1.0)
    if not quiet:
        print(f"Loaded artifacts: semantic={len(ctx['semantic'])}, "
              f"reranker={len(ctx.get('reranker', {}))}", file=sys.stderr)
    return ctx


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
    context = load_context(args.artifacts, quiet=args.quiet, lexical_only=args.lexical_only)
    heap: list[tuple] = []          # min-heap of (score, candidate_id, counter)
    payloads: dict[int, tuple] = {} # counter -> (scored, candidate)
    counter = 0
    n_total = n_honeypot = 0

    for cand in data_loader.iter_candidates(args.candidates):
        n_total += 1
        if honeypot.is_honeypot(cand):       # force impossible profiles out of contention (DQ safety)
            n_honeypot += 1
            continue
        scored = scoring.score_candidate(cand, context)
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
    # Normalize displayed scores to [0,1] (rank-1 -> 1.0). The bounded behavioral multiplier can push
    # raw fit slightly above 1.0; rescaling by a positive constant preserves the ranking, ties and the
    # non-increasing property while matching the spec's 0-1 score convention.
    norm = top[0]["score"] if (top and top[0]["score"] > 0) else 1.0
    rows = []
    for s in top:
        cand = cand_by_id[s["candidate_id"]]
        rows.append({
            "candidate_id": s["candidate_id"],
            "rank": s["rank"],
            "score": min(1.0, s["score"] / norm),
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
