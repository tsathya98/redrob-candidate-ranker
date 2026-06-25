"""Feature extraction per candidate (inputs to scoring.py).

Turns raw profiles into measurable signals; no weighting/combination here (that's scoring.py).
Pure functions, CPU-only, no network. See docs/05 components B-E + behavioral.
"""

from __future__ import annotations

from .data_loader import parse_date
from . import jd_profile as jd


def substance_text(candidate: dict) -> str:
    """Free text where *substance* lives: summary + headline + career titles + descriptions.

    Deliberately EXCLUDES the skills list — so a keyword-stuffer who merely lists AI skills does not
    get relevance credit here (docs/03 Trap 1). Skills are scored separately and gated by role.
    """
    p = candidate.get("profile", {})
    parts = [p.get("summary", ""), p.get("headline", ""), p.get("current_title", "")]
    for job in candidate.get("career_history", []):
        parts.append(job.get("title", ""))
        parts.append(job.get("description", ""))
    return " ".join(s for s in parts if s).lower()


def title_career_features(candidate: dict) -> dict:
    """Engineering-role plausibility, concept evidence, and product-vs-services signal."""
    p = candidate.get("profile", {})
    titles = [p.get("current_title", "")] + [j.get("title", "") for j in candidate.get("career_history", [])]
    role = max((jd.role_relevance(t) for t in titles), default=jd.DEFAULT_ROLE_RELEVANCE)

    companies = [(j.get("company") or "").lower() for j in candidate.get("career_history", [])]
    sizes = [j.get("company_size", "") for j in candidate.get("career_history", [])]
    n = max(len(companies), 1)
    services_hits = sum(1 for c in companies if any(f in c for f in jd.SERVICES_FIRMS))
    services_fraction = services_hits / n
    # a product company = not a known services firm and not a tiny/no-name (heuristic: any non-services co)
    has_product = any(c and not any(f in c for f in jd.SERVICES_FIRMS) for c in companies)

    hits = jd.concept_hits(substance_text(candidate))
    return {
        "role_relevance": role,
        "services_fraction": services_fraction,
        "services_only": services_fraction == 1.0 and not has_product,
        "has_product": has_product,
        "concept_hits": hits,
        "company_sizes": sizes,
    }


def experience_features(candidate: dict) -> dict:
    """Distance from the 5-9 (ideal 6-8) experience band."""
    yoe = candidate.get("profile", {}).get("years_of_experience") or 0.0
    lo, hi = jd.IDEAL_EXPERIENCE
    blo, bhi = jd.EXPERIENCE_BAND
    if lo <= yoe <= hi:
        fit = 1.0
    elif blo <= yoe <= bhi:
        fit = 0.85
    else:
        # linear falloff outside the band, floored at 0.1
        dist = (blo - yoe) if yoe < blo else (yoe - bhi)
        fit = max(0.1, 0.85 - 0.12 * dist)
    return {"yoe": yoe, "experience_fit": round(fit, 4)}


_PROF_W = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.85, "expert": 1.0}


def skill_depth_features(candidate: dict) -> dict:
    """Depth of *relevant* skills: proficiency x endorsement/duration trust, corroborated by assessments.

    Not raw count — a long AI skill list with no endorsements/duration earns little (lazy stuffing).
    """
    assessments = candidate.get("redrob_signals", {}).get("skill_assessment_scores", {}) or {}
    total = 0.0
    relevant = []
    for sk in candidate.get("skills", []):
        name = (sk.get("name") or "").lower()
        if not any(rk in name for rk in jd.RELEVANT_SKILLS):
            continue
        prof = _PROF_W.get(sk.get("proficiency", ""), 0.4)
        endorse = min(1.0, (sk.get("endorsements", 0) or 0) / 30.0)
        dur = min(1.0, (sk.get("duration_months", 0) or 0) / 36.0)
        trust = 0.4 + 0.6 * (0.5 * endorse + 0.5 * dur)  # 0.4..1.0
        assess = assessments.get(sk.get("name"))
        assess_factor = 1.0 if assess is None else (0.6 + 0.4 * min(1.0, assess / 80.0))
        contrib = prof * trust * assess_factor
        total += contrib
        relevant.append((sk.get("name"), round(contrib, 3)))
    # saturating: ~4-5 strong relevant skills -> near 1.0
    depth = 1.0 - pow(2.718281828, -total / 2.5)
    relevant.sort(key=lambda x: -x[1])
    return {"skill_depth": round(depth, 4), "relevant_skills": relevant[:8], "n_relevant": len(relevant)}


_TIER_W = {"tier_1": 1.0, "tier_2": 0.78, "tier_3": 0.58, "tier_4": 0.4, "unknown": 0.45}
_RELEVANT_FIELDS = ("computer science", "artificial intelligence", "machine learning", "data science",
                    "information", "mathematics", "statistics", "electronics", "software")


def education_features(candidate: dict) -> dict:
    """Institution tier + field relevance + a small certification bonus."""
    best_tier = 0.45
    field_bonus = 0.0
    for ed in candidate.get("education", []):
        best_tier = max(best_tier, _TIER_W.get(ed.get("tier", "unknown"), 0.45))
        fos = (ed.get("field_of_study") or "").lower()
        if any(f in fos for f in _RELEVANT_FIELDS):
            field_bonus = 0.15
    certs = candidate.get("certifications", []) or []
    cert_bonus = min(0.1, 0.03 * len(certs))
    score = min(1.0, 0.7 * best_tier + field_bonus + cert_bonus)
    return {"education": round(score, 4), "best_tier": best_tier, "n_certs": len(certs)}


def location_features(candidate: dict) -> dict:
    """Location fit: Pune/Noida > other Tier-1 Indian metros > elsewhere India > outside India (+relocate)."""
    p = candidate.get("profile", {})
    loc = (p.get("location") or "").lower()
    country = (p.get("country") or "").lower()
    relocate = bool(candidate.get("redrob_signals", {}).get("willing_to_relocate"))
    in_india = "india" in country
    if any(c in loc for c in jd.PREFERRED_LOCATIONS):
        fit = 1.0
    elif any(c in loc for c in jd.ACCEPTABLE_INDIAN_METROS):
        fit = 0.85
    elif in_india:
        fit = 0.7 if relocate else 0.6
    else:
        fit = 0.45 if relocate else 0.3  # outside India: case-by-case, no visa sponsorship
    return {"location_fit": fit, "in_india": in_india, "willing_to_relocate": relocate}


def tenure_features(candidate: dict) -> dict:
    """Job-hopping / title-chaser signal: many short stints."""
    durs = [j.get("duration_months", 0) or 0 for j in candidate.get("career_history", [])
            if not j.get("is_current")]
    short = sum(1 for d in durs if 0 < d < 18)
    chaser = len(durs) >= 3 and short >= 3
    return {"n_past_roles": len(durs), "short_stints": short, "title_chaser": chaser}


def behavioral_features(candidate: dict) -> dict:
    """Availability/quality signals from redrob_signals (docs/02). Handles -1 sentinels as 'unknown'."""
    s = candidate.get("redrob_signals", {})
    return {
        "recruiter_response_rate": s.get("recruiter_response_rate", 0.0) or 0.0,
        "open_to_work": bool(s.get("open_to_work_flag")),
        "interview_completion_rate": s.get("interview_completion_rate", 0.0) or 0.0,
        "saved_by_recruiters_30d": s.get("saved_by_recruiters_30d", 0) or 0,
        "notice_period_days": s.get("notice_period_days", 180) or 180,
        "last_active_date": s.get("last_active_date"),
        "profile_completeness": s.get("profile_completeness_score", 0) or 0,
    }
