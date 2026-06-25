"""Score combination and final ranking (docs/05_approach_and_roadmap.md).

Combines the components into one explainable score per candidate and keeps the full breakdown so
reasoning.py (and the demo UI) can show *why*. CPU-only, no network.

Slice 1 (baseline, no embeddings):
    relevance     = weighted concept coverage in career substance (semantic-ish recall)
    title_career  = engineering-role plausibility + product-vs-services  (Trap 1 defense)
    experience    = 5-9 band fit
    skill_depth   = depth of relevant skills, GATED by role relevance (Trap 1 defense)
    education     = institution tier + field + certs
  x behavioral availability modifier (bounded)   x soft penalties (services/cv-speech/title-chaser/location)

Slice 2 will blend a semantic embedding score into `relevance`.
"""

from __future__ import annotations

import math

from . import features as F
from . import jd_profile as jd
from .data_loader import parse_date
from .honeypot import REFERENCE_DATE

_POS_WEIGHT_SUM = sum(w for w in jd.CONCEPT_WEIGHTS.values() if w > 0)
_RELEVANCE_DENOM = 0.55 * _POS_WEIGHT_SUM  # strong (3-5 category) candidates approach ~0.8


def _relevance_from_hits(hits: dict[str, int]) -> tuple[float, list[str]]:
    """Weighted, saturating concept coverage -> (score in [0,1], matched category list)."""
    raw = 0.0
    matched = []
    for cat, count in hits.items():
        w = jd.CONCEPT_WEIGHTS.get(cat, 0.0)
        if w <= 0:
            continue
        raw += w * (1.0 - math.exp(-count / 2.0))
        matched.append(cat)
    return min(1.0, raw / _RELEVANCE_DENOM), matched


def _behavioral_modifier(bf: dict) -> tuple[float, list[str]]:
    """Map availability signals to a bounded multiplier and collect honest concerns."""
    # recency of activity
    last = parse_date(bf.get("last_active_date"))
    if last is not None:
        days = (REFERENCE_DATE - last).days
        recency = max(0.0, min(1.0, 1.0 - max(0, days - 60) / 305.0))
    else:
        recency = 0.5

    notice = bf.get("notice_period_days", 180)
    raw = (
        0.30 * bf.get("recruiter_response_rate", 0.0)
        + 0.20 * recency
        + 0.15 * (1.0 if bf.get("open_to_work") else 0.0)
        + 0.15 * bf.get("interview_completion_rate", 0.0)
        + 0.10 * min(1.0, bf.get("saved_by_recruiters_30d", 0) / 10.0)
        + 0.10 * (1.0 - min(1.0, notice / 120.0))
    )
    lo, hi = jd.BEHAVIORAL_MODIFIER_RANGE
    modifier = lo + (hi - lo) * raw

    concerns = []
    if bf.get("recruiter_response_rate", 0.0) < 0.2:
        concerns.append(f"low recruiter response rate ({bf.get('recruiter_response_rate', 0):.0%})")
    if recency < 0.4:
        concerns.append("not recently active on platform")
    if not bf.get("open_to_work"):
        concerns.append("not flagged open-to-work")
    if notice and notice > 60:
        concerns.append(f"{notice}-day notice period")
    return round(modifier, 4), concerns


def score_candidate(candidate: dict, context: dict | None = None) -> dict:
    """Return {'score', 'components', 'modifier', 'penalties', 'concerns', 'evidence', ...}."""
    tc = F.title_career_features(candidate)
    exp = F.experience_features(candidate)
    sk = F.skill_depth_features(candidate)
    ed = F.education_features(candidate)
    loc = F.location_features(candidate)
    ten = F.tenure_features(candidate)
    bf = F.behavioral_features(candidate)

    lexical, matched = _relevance_from_hits(tc["concept_hits"])

    # --- Slice 2: blend in precomputed semantic similarity (relevance) and cross-encoder rerank (fit) ---
    ctx = context or {}
    cid = candidate["candidate_id"]
    sem = ctx.get("semantic")
    rer = ctx.get("reranker")
    rr_lo, rr_hi = ctx.get("rerank_range", (0.0, 1.0))

    sem_norm = None
    if sem is not None and cid in sem:
        sem_norm = max(0.0, min(1.0, (sem[cid] + 1.0) / 2.0))  # cosine [-1,1] -> [0,1]
    rer_norm = None
    if rer is not None and cid in rer:
        rer_norm = (rer[cid] - rr_lo) / (rr_hi - rr_lo) if rr_hi > rr_lo else 0.5
        rer_norm = max(0.0, min(1.0, rer_norm))

    # relevance component = lexical (Slice 1) blended with semantic recall (Slice 2)
    relevance = lexical if sem_norm is None else (0.5 * lexical + 0.5 * sem_norm)
    relevance_parts = {"lexical": round(lexical, 4)}
    if sem_norm is not None:
        relevance_parts["semantic"] = round(sem_norm, 4)
    if rer_norm is not None:
        relevance_parts["rerank"] = round(rer_norm, 4)

    # skill depth is gated by engineering-role plausibility (stuffer defense)
    skill_gated = sk["skill_depth"] * (0.3 + 0.7 * tc["role_relevance"])

    # title/career: role plausibility, with a product bonus / services drag folded in
    title_career = tc["role_relevance"] * (1.0 + 0.0)  # base; services handled as penalty below
    if tc["has_product"]:
        title_career = min(1.0, title_career + 0.05)

    components = {
        "relevance": round(relevance, 4),
        "title_career": round(title_career, 4),
        "experience": exp["experience_fit"],
        "skill_depth": round(skill_gated, 4),
        "education": ed["education"],
    }
    base = sum(jd.COMPONENT_WEIGHTS[k] * v for k, v in components.items())

    # cross-encoder reranker (when available for this candidate) takes authority over the top tier:
    # half the pre-penalty fit becomes the cross-encoder relevance. Stuffers score low on BOTH, so they
    # still sink; honeypots are excluded upstream. (docs/06 retrieve-and-rerank.)
    fit = base if rer_norm is None else (0.5 * base + 0.5 * rer_norm)

    # --- soft penalties (multiplicative) ---
    penalties = []
    pmult = 1.0
    if tc["services_only"]:
        pmult *= 0.45
        penalties.append("entire career at services/consulting firms")
    # CV/speech-only: cv/speech present but no NLP/IR or retrieval/ranking evidence
    hits = tc["concept_hits"]
    if hits.get("cv_speech_robotics") and not (hits.get("nlp_ir") or hits.get("embeddings_retrieval")
                                               or hits.get("ranking_recsys")):
        pmult *= 0.6
        penalties.append("CV/speech focus without NLP/IR")
    if ten["title_chaser"]:
        pmult *= 0.85
        penalties.append("frequent short stints (title-chaser pattern)")
    # location as a mild multiplier
    pmult *= 0.85 + 0.15 * loc["location_fit"]
    if not loc["in_india"]:
        penalties.append("based outside India (no visa sponsorship)")

    modifier, bconcerns = _behavioral_modifier(bf)

    score = fit * pmult * modifier

    return {
        "candidate_id": candidate["candidate_id"],
        "score": round(score, 6),
        "base": round(base, 4),
        "fit": round(fit, 4),
        "reranked": rer_norm is not None,
        "components": components,
        "modifier": modifier,
        "penalty_multiplier": round(pmult, 4),
        "penalties": penalties,
        "concerns": penalties + bconcerns,
        "matched_concepts": matched,
        "evidence": {
            "role_relevance": tc["role_relevance"],
            "relevant_skills": sk["relevant_skills"],
            "yoe": exp["yoe"],
            "has_product": tc["has_product"],
            "location_fit": loc["location_fit"],
            "relevance_parts": relevance_parts,
        },
    }


def rank_pool(scored: list[dict], top_n: int = 100) -> list[dict]:
    """Sort by score desc, tie-break candidate_id asc; assign ranks 1..top_n.

    Mirrors validate_submission.py's tie-break so output passes format validation, and guarantees
    monotonic non-increasing scores by construction.
    """
    ordered = sorted(scored, key=lambda d: (-d["score"], d["candidate_id"]))[:top_n]
    for i, d in enumerate(ordered, start=1):
        d["rank"] = i
    return ordered
