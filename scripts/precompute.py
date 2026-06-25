#!/usr/bin/env python3
"""OFFLINE precompute (Slice 2) — semantic embeddings + cross-encoder reranker.

The JD is FIXED, so everything that needs a model runs here, once, offline, and is cached to JSON.
`rank.py` then reads only the JSON (stdlib) and stays CPU-only / offline / <5 min.

Outputs (to --out dir):
  semantic.json   {candidate_id: cosine(JD, candidate)}        for ALL candidates
  reranker.json   {candidate_id: cross_encoder_score}          for the top-K shortlist
  meta.json       models, shortlist size, counts

Usage:
  uv pip install torch --index-url https://download.pytorch.org/whl/cpu
  uv pip install -r requirements-precompute.txt
  uv run python scripts/precompute.py --candidates data/candidates.jsonl --out artifacts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import data_loader, honeypot, scoring  # noqa: E402
from src import features as F  # noqa: E402
from src import jd_profile as jd  # noqa: E402

# bge-small-en-v1.5 asymmetric retrieval: instruction goes on the QUERY (the JD) only.
BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def embed_text(candidate: dict) -> str:
    """Text to embed = career substance (NOT the raw skills list — keeps the stuffer defense)."""
    return F.substance_text(candidate)[:2000]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Precompute semantic + reranker artifacts (offline).")
    p.add_argument("--candidates", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--embed-pool", type=int, default=4000,
                   help="Top-N by Slice-1 score to embed (recall funnel; rest can't reach top-100).")
    p.add_argument("--shortlist", type=int, default=600, help="Top-K to cross-encoder rerank.")
    p.add_argument("--embed-model", default="BAAI/bge-small-en-v1.5")
    p.add_argument("--rerank-model", default="BAAI/bge-reranker-v2-m3")
    p.add_argument("--limit", type=int, default=0, help="Only process first N candidates (debug).")
    p.add_argument("--batch-size", type=int, default=128)
    args = p.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    import os
    import torch
    from sentence_transformers import CrossEncoder, SentenceTransformer

    torch.set_num_threads(os.cpu_count() or 4)

    # --- recall funnel: score everyone with the fast Slice-1 ranker, keep the top embed-pool ---
    # (a true fit always lands well within the top few-thousand by structured score, so embedding only
    # the pool is safe; everyone else cannot reach the top-100 anyway. This avoids embedding all 100k.)
    scored = []
    n_total = n_hp = 0
    for i, c in enumerate(data_loader.iter_candidates(args.candidates)):
        if args.limit and i >= args.limit:
            break
        n_total += 1
        if honeypot.is_honeypot(c):
            n_hp += 1
            continue
        base = scoring.score_candidate(c)["score"]
        scored.append((base, c["candidate_id"], c))
    scored.sort(key=lambda t: -t[0])
    pool = scored[: args.embed_pool]
    print(f"scored {n_total} ({n_hp} honeypots); embedding top {len(pool)} of them", file=sys.stderr)

    base_by_id = {cid: b for b, cid, _ in pool}
    texts = [embed_text(c) for _, _, c in pool]
    pool_ids = [cid for _, cid, _ in pool]
    cand_by_id = {cid: c for _, cid, c in pool}

    # --- stage 1: bi-encoder embeddings + cosine to the fixed JD (pool only) ---
    print(f"embedding with {args.embed_model} ...", file=sys.stderr)
    embedder = SentenceTransformer(args.embed_model)
    jd_vec = embedder.encode([BGE_QUERY_INSTRUCTION + jd.jd_query_text()],
                             normalize_embeddings=True)[0]
    doc_vecs = embedder.encode(texts, batch_size=args.batch_size, normalize_embeddings=True,
                               show_progress_bar=True)
    cos = (doc_vecs @ jd_vec).tolist()  # normalized -> dot == cosine
    semantic = {cid: round(float(s), 5) for cid, s in zip(pool_ids, cos)}

    # --- pick the rerank shortlist: blend Slice-1 base + semantic ---
    def sem_norm(cid: str) -> float:
        return max(0.0, min(1.0, (semantic[cid] + 1.0) / 2.0))

    prelim = sorted(((0.6 * base_by_id[cid] + 0.4 * sem_norm(cid), cid) for cid in pool_ids),
                    reverse=True)
    shortlist = [cid for _, cid in prelim[: args.shortlist]]
    print(f"reranking top {len(shortlist)} with {args.rerank_model} ...", file=sys.stderr)

    # --- stage 2: cross-encoder rerank the shortlist (offline; JD is fixed) ---
    reranker = CrossEncoder(args.rerank_model, max_length=512)
    pairs = [(jd.jd_query_text(), embed_text(cand_by_id[cid])) for cid in shortlist]
    scores = reranker.predict(pairs, batch_size=16, show_progress_bar=True)
    reranker_scores = {cid: round(float(s), 5) for cid, s in zip(shortlist, scores)}

    # --- write artifacts ---
    (args.out / "semantic.json").write_text(json.dumps(semantic))
    (args.out / "reranker.json").write_text(json.dumps(reranker_scores))
    (args.out / "meta.json").write_text(json.dumps({
        "embed_model": args.embed_model,
        "rerank_model": args.rerank_model,
        "n_scored": n_total,
        "n_embedded": len(pool_ids),
        "n_honeypots": n_hp,
        "shortlist": len(shortlist),
        "query_instruction": BGE_QUERY_INSTRUCTION,
    }, indent=2))
    print(f"wrote artifacts to {args.out}/ (semantic={len(semantic)}, reranker={len(reranker_scores)})",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
