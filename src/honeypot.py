"""Honeypot / impossibility detection (docs/03_traps_and_honeypots.md, Trap 4).

~80 candidates have logically impossible profiles and are forced to ground-truth relevance tier 0.
Ranking any in the top-100 risks the >10%-in-top-100 disqualification, so this is a safety net:
flag impossible profiles and force them to the bottom.

Verified signature (full-pool scan): 21 candidates have an expert-proficiency skill at 0-month duration.
Honeypots typically combine multiple impossibilities; tune thresholds to flag the ~80 without false positives.
"""

from __future__ import annotations


def impossibility_flags(candidate: dict) -> list[str]:
    """Return a list of triggered impossibility reasons for a candidate (empty == clean).

    Planned checks (Phase 2):
      - expert/advanced proficiency with duration_months == 0
      - duration_months inconsistent with start_date/end_date span
      - sum of career tenures implausible vs years_of_experience
      - start_date > end_date; is_current True but end_date set
      - education start_year > end_year
      - overlapping full-time current roles beyond the timeline
      - self-rated 'expert' contradicted by near-zero skill_assessment_scores
    """
    raise NotImplementedError("Phase 2: implement impossibility checks.")


def is_honeypot(candidate: dict, threshold: int = 1) -> bool:
    """Whether a candidate should be treated as a honeypot (force to bottom).

    TODO(Phase 2): calibrate `threshold` (single hard contradiction vs combination) against the ~80 target
    so legitimate profiles are not wrongly excluded.
    """
    raise NotImplementedError("Phase 2: implement honeypot decision.")
