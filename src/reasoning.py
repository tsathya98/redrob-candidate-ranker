"""Per-candidate reasoning generation (docs/04 Stage-4 rubric).

Produces the 1-2 sentence `reasoning` column from the *actual* score components and profile facts.
Must satisfy the manual-review checks: specific facts, JD connection, honest concerns, NO hallucination,
variation across candidates, and rank-consistent tone.

Strictly template-from-real-data (no LLM, no network): every clause is sourced from a value that exists
in the candidate's profile or its computed components, so it cannot hallucinate.
"""

from __future__ import annotations


def build_reasoning(candidate: dict, scored: dict, rank: int) -> str:
    """Return a 1-2 sentence justification grounded in real facts and the score breakdown.

    Inputs:
      - candidate: the raw profile (source of facts: YOE, current_title, named skills, signal values)
      - scored: output of scoring.score_candidate (components, penalties, concerns)
      - rank: final rank (tone must match: strong at top, hedged/critical lower)

    TODO(Phase 6): assemble fact phrases + JD-connection clause + honest-concern clause; vary phrasing by
    candidate; scale tone to rank. Guarantee no claim references data not present in `candidate`.
    """
    raise NotImplementedError("Phase 6: implement reasoning generation.")
