"""Score combination and final ranking (docs/05_approach_and_roadmap.md).

Combines the components into one explainable score per candidate:
    A semantic relevance (embeddings + BM25)   -- Phase 4
    B title/career fit                          -- Phase 3
    C experience-band fit                       -- Phase 3
    D skill depth (corroborated)                -- Phase 3
    E education/cert prior                       -- Phase 3
    JD hard-gates / soft-penalties               -- Phase 3
    x behavioral availability modifier           -- Phase 5

The component breakdown is retained per candidate so reasoning.py can cite *why* (no black box).
Final ranking honors the submission tie-break (equal score -> candidate_id ascending).
"""

from __future__ import annotations

# Initial hand-set weights — every value justified in docs/PROJECT_LOG.md as it is tuned.
# (Relevance dominates; behavioral is a bounded multiplier, not an additive component.)
COMPONENT_WEIGHTS = {
    "semantic": 0.30,
    "title_career": 0.30,
    "experience": 0.12,
    "skill_depth": 0.18,
    "education": 0.10,
}
BEHAVIORAL_MODIFIER_RANGE = (0.5, 1.15)  # bounded so availability modulates, never overrides relevance


def score_candidate(candidate: dict, context: dict) -> dict:
    """Return {'score': float, 'components': {...}, 'penalties': [...], 'concerns': [...]}.

    `context` carries precomputed shared state (JD embedding, BM25 index, idf, etc.).
    TODO(Phase 3-5): assemble components, apply gates/penalties, apply behavioral modifier.
    """
    raise NotImplementedError("Phase 3-5: implement scoring.")


def rank_pool(scored: list[dict], top_n: int = 100) -> list[dict]:
    """Sort by score descending, tie-break by candidate_id ascending, take top_n.

    Mirrors validate_submission.py's tie-break so output passes format validation.
    TODO(Phase 7): implement and assert monotonic non-increasing scores by rank.
    """
    raise NotImplementedError("Phase 7: implement ranking + tie-break.")
