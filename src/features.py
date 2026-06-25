"""Feature extraction per candidate (inputs to scoring.py).

Turns raw profiles into the structured signals the scoring components consume
(docs/05_approach_and_roadmap.md, components B-E + behavioral). No scoring/weighting here —
just measurable features. Pure functions, CPU-only, no network.
"""

from __future__ import annotations


def title_career_features(candidate: dict) -> dict:
    """Engineering-role plausibility + recsys/search/ranking evidence + product-vs-services.

    TODO(Phase 3): is the title an engineering role? do career descriptions show building
    ranking/search/recsys at a product company? services-only career? title-chaser tenure pattern?
    """
    raise NotImplementedError("Phase 3.")


def experience_features(candidate: dict) -> dict:
    """Distance from the 5-9 (ideal 6-8) experience band; recency of hands-on production work."""
    raise NotImplementedError("Phase 3.")


def skill_depth_features(candidate: dict) -> dict:
    """Skill depth, not count: proficiency x endorsements x duration, corroborated by
    redrob_signals.skill_assessment_scores. Flags self-rating vs assessment mismatches (stuffers)."""
    raise NotImplementedError("Phase 3.")


def education_features(candidate: dict) -> dict:
    """Institution tier + field-of-study relevance + certifications (mild prior)."""
    raise NotImplementedError("Phase 3.")


def behavioral_features(candidate: dict) -> dict:
    """Availability/quality signals from redrob_signals (docs/02): response rate, last_active recency,
    open_to_work, interview_completion, saved_by_recruiters, notice period, relocation. Handles -1 sentinels."""
    raise NotImplementedError("Phase 5.")


def location_features(candidate: dict) -> dict:
    """Location fit: Pune/Noida > other Tier-1 Indian metros > elsewhere-in-India > outside-India;
    factor in willing_to_relocate."""
    raise NotImplementedError("Phase 3.")
