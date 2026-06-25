#!/usr/bin/env python3
"""CLI entry point — the single reproduce command (docs/04 Section 10.3).

    python src/rank.py --candidates ./candidates.jsonl --out ./submission.csv

Orchestrates the pipeline (docs/05): load -> honeypot filter -> score -> rank top-100 -> reason -> write CSV.
Must run CPU-only, no network, <=5 min, <=16 GB. Embeddings are precomputed offline (see --embeddings).

Pipeline logic is implemented across Phases 1-7; this file currently wires the CLI and pipeline skeleton
so `--help` works and the reproduce command is stable from day one.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REQUIRED_HEADER = ["candidate_id", "rank", "score", "reasoning"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rank.py",
        description="Rank the top-100 best-fit candidates for the Redrob Senior AI Engineer JD.",
    )
    p.add_argument("--candidates", required=True, type=Path,
                   help="Path to candidates.jsonl (or .jsonl.gz).")
    p.add_argument("--out", required=True, type=Path,
                   help="Output CSV path (candidate_id,rank,score,reasoning).")
    p.add_argument("--embeddings", type=Path, default=None,
                   help="Optional path to precomputed candidate embeddings artifact (Phase 4).")
    p.add_argument("--top-n", type=int, default=100,
                   help="Number of candidates to output (challenge requires exactly 100).")
    return p.parse_args(argv)


def write_submission(rows: list[dict], out_path: Path) -> None:
    """Write the ranked rows to a spec-compliant CSV (header + exactly top-n data rows)."""
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REQUIRED_HEADER)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in REQUIRED_HEADER})


def run(args: argparse.Namespace) -> list[dict]:
    """Execute the ranking pipeline. Implemented across Phases 1-7."""
    # from . import data_loader, honeypot, jd_profile, scoring, reasoning
    raise NotImplementedError(
        "Ranking pipeline not yet implemented — see docs/05_approach_and_roadmap.md phases 1-7."
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows = run(args)
    write_submission(rows, args.out)
    print(f"Wrote {len(rows)} ranked candidates to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
