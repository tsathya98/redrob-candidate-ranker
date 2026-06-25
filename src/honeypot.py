"""Honeypot / impossibility detection (docs/03_traps_and_honeypots.md, Trap 4).

~80 candidates have logically impossible profiles and are forced to ground-truth relevance tier 0.
Ranking any in the top-100 risks the >10%-in-top-100 disqualification, so this is a safety net:
flag impossible profiles and force them to the bottom.

Design: each check returns a reason string. Some contradictions are *hard* (unambiguous data
impossibilities) and mark a honeypot on their own; others are *soft* and only count in combination.
Thresholds are calibrated against the pool (see scripts/calibrate_honeypots via the module's stats helper).
"""

from __future__ import annotations

from datetime import date

from .data_loader import months_between, parse_date

# Reference "now" for evaluating current-role durations (just after the pool's latest activity).
REFERENCE_DATE = date(2026, 6, 30)

# Tolerances (months) — generous, so we flag genuine impossibilities, not rounding noise.
DURATION_SPAN_TOLERANCE = 9
EXPERIENCE_SPAN_TOLERANCE_YEARS = 2.5

# A hard flag marks a honeypot on its own; soft flags must accumulate (see is_honeypot).
# Each hard flag is a logical impossibility that, on this pool, is cleanly separated from legitimate
# profiles by a wide gap (verified: yoe-vs-career-span and duration-vs-span have empty middle ranges).
# NOTE: a "skill duration > career length" check was tried and rejected — it fires on ~9% of the pool,
# i.e. it is a normal characteristic of this synthetic data, not a honeypot signal.
HARD_FLAGS = {
    "career_dates_reversed",
    "current_role_has_end_date",
    "education_years_reversed",
    "expert_skill_zero_duration",
    "duration_exceeds_span",
    "experience_exceeds_career_span",
}


def impossibility_flags(candidate: dict) -> list[str]:
    """Return triggered impossibility reasons (empty == internally consistent)."""
    flags: list[str] = []
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience") or 0.0

    # --- career history date/tenure consistency ---
    starts: list[date] = []
    ends: list[date] = []
    for job in candidate.get("career_history", []):
        start = parse_date(job.get("start_date"))
        end = parse_date(job.get("end_date"))
        is_current = job.get("is_current", False)
        dur = job.get("duration_months")

        if start:
            starts.append(start)
        ends.append(end or REFERENCE_DATE)

        if start and end and start > end:
            flags.append("career_dates_reversed")
        if is_current and end is not None:
            flags.append("current_role_has_end_date")

        # stated duration vs actual span (use REFERENCE_DATE for ongoing roles)
        span = months_between(start, end or REFERENCE_DATE)
        if span is not None and dur is not None and dur - span > DURATION_SPAN_TOLERANCE:
            flags.append("duration_exceeds_span")

    # total career span vs claimed years_of_experience
    if starts:
        span_years = (max(ends) - min(starts)).days / 365.25
        if yoe - span_years > EXPERIENCE_SPAN_TOLERANCE_YEARS:
            flags.append("experience_exceeds_career_span")

    # --- skills: proficiency vs duration, and skill duration vs career length ---
    assessments = candidate.get("redrob_signals", {}).get("skill_assessment_scores", {}) or {}
    for sk in candidate.get("skills", []):
        prof = sk.get("proficiency")
        dur = sk.get("duration_months", 0) or 0
        if prof in ("expert", "advanced") and dur == 0:
            flags.append("expert_skill_zero_duration")
        # self-rated expert contradicted by a near-zero platform assessment (soft signal)
        score = assessments.get(sk.get("name"))
        if prof == "expert" and score is not None and score < 20:
            flags.append("expert_skill_failed_assessment")

    # --- education sanity ---
    for ed in candidate.get("education", []):
        sy, ey = ed.get("start_year"), ed.get("end_year")
        if isinstance(sy, int) and isinstance(ey, int):
            if sy > ey:
                flags.append("education_years_reversed")
            elif ey - sy > 15:
                flags.append("education_span_implausible")

    return flags


def is_honeypot(candidate: dict, min_soft_flags: int = 2) -> bool:
    """True if the candidate should be forced to the bottom.

    A single *hard* contradiction is enough; otherwise require >= min_soft_flags distinct soft flags.
    """
    flags = set(impossibility_flags(candidate))
    if flags & HARD_FLAGS:
        return True
    return len(flags) >= min_soft_flags
