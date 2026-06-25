"""Service layer: turn the offline ranker into UI-friendly payloads.

Reuses src/ (scoring, honeypot, features, jd_profile, reasoning). Pure-Python, CPU, no network.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from src import features as F
from src import honeypot, reasoning, scoring
from src import jd_profile as jd

# JD must-have concept categories (for gap analysis).
MUST_HAVE_CONCEPTS = ["embeddings_retrieval", "vector_db_hybrid_search", "ranking_recsys", "ranking_eval"]

_CONCEPT_LABEL = {
    "embeddings_retrieval": "Embeddings & retrieval",
    "vector_db_hybrid_search": "Vector DB / hybrid search",
    "ranking_recsys": "Ranking & recommendation",
    "ranking_eval": "Ranking evaluation (NDCG/A-B)",
    "ml_production": "Production ML at scale",
    "nlp_ir": "NLP / IR",
    "llm": "LLM fine-tuning / RAG",
    "cv_speech_robotics": "CV / speech / robotics",
}

# Human-facing JD rubric for the "JD Intelligence" panel (mirrors docs/01 + docs/07).
JD_RUBRIC = {
    "title": "Senior AI Engineer — Founding Team @ Redrob AI",
    "experience_band": "5–9 yrs (ideal 6–8)",
    "location": "Pune/Noida or Tier-1 India (or willing to relocate)",
    "must_have": [
        {"name": "Production embeddings-based retrieval", "weight": 1.0},
        {"name": "Vector DB / hybrid search", "weight": 0.9},
        {"name": "Ranking / recommendation systems", "weight": 1.0},
        {"name": "Ranking evaluation (NDCG, MRR, A/B)", "weight": 0.8},
        {"name": "Strong Python at a product company", "weight": 0.9},
    ],
    "nice_to_have": [
        {"name": "LLM fine-tuning (LoRA/QLoRA/PEFT)"},
        {"name": "Learning-to-rank (XGBoost/neural)"},
        {"name": "HR-tech / marketplace domain"},
        {"name": "Distributed systems / inference at scale"},
        {"name": "Open-source AI/ML contributions"},
    ],
    "negative": [
        {"name": "Services/consulting-only career", "penalty": "×0.45"},
        {"name": "CV/speech/robotics without NLP/IR", "penalty": "×0.6"},
        {"name": "Title-chaser (frequent <18mo stints)", "penalty": "×0.85"},
        {"name": "Pure research, no production"},
        {"name": "Recent-LLM-only, no pre-LLM ML"},
    ],
    "component_weights": jd.COMPONENT_WEIGHTS,
}


def load_candidates(path: str | Path) -> list[dict]:
    out = []
    with open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _brief(c: dict) -> dict:
    p = c.get("profile", {})
    return {
        "candidate_id": c["candidate_id"],
        "name": p.get("anonymized_name", ""),
        "title": p.get("current_title", ""),
        "company": p.get("current_company", ""),
        "country": p.get("country", ""),
        "location": p.get("location", ""),
        "yoe": p.get("years_of_experience", 0),
    }


def _naive_score(c: dict) -> int:
    """The naive keyword-stuffer metric: how many JD-relevant skills are *listed* (no role gating)."""
    return sum(1 for s in c.get("skills", [])
               if any(rk in (s.get("name") or "").lower() for rk in jd.RELEVANT_SKILLS))


def rank_candidates(candidates: list[dict]) -> dict:
    """Rank a sample. Returns ranked list (honeypots flagged + forced to bottom) + naive comparison."""
    scored_rows = []
    honeypot_rows = []
    for c in candidates:
        if honeypot.is_honeypot(c):
            honeypot_rows.append({
                **_brief(c), "status": "honeypot_filtered", "score": 0.0,
                "honeypot_flags": honeypot.impossibility_flags(c),
                "naive_score": _naive_score(c),
            })
            continue
        s = scoring.score_candidate(c)
        scored_rows.append((c, s))

    ranked = scoring.rank_pool([s for _, s in scored_rows], top_n=len(scored_rows))
    cand_by_id = {c["candidate_id"]: c for c, _ in scored_rows}

    results = []
    for s in ranked:
        c = cand_by_id[s["candidate_id"]]
        results.append({
            **_brief(c),
            "status": "ranked",
            "rank": s["rank"],
            "score": s["score"],
            "components": s["components"],
            "modifier": s["modifier"],
            "penalty_multiplier": s["penalty_multiplier"],
            "concerns": s["concerns"],
            "matched_concepts": [_CONCEPT_LABEL.get(x, x) for x in s["matched_concepts"]],
            "reasoning": reasoning.build_reasoning(c, s, s["rank"]),
            "naive_score": _naive_score(c),
        })

    # naive keyword ranking (what an ATS / stuffer-friendly ranker would do)
    naive = sorted(candidates, key=lambda c: -_naive_score(c))
    naive_top10 = [c["candidate_id"] for c in naive[:10]]
    smart_top10 = [r["candidate_id"] for r in results[:10]]

    return {
        "results": results,
        "honeypots": honeypot_rows,
        "stats": {
            "total": len(candidates),
            "ranked": len(results),
            "honeypots_filtered": len(honeypot_rows),
            "naive_top10": naive_top10,
            "smart_top10": smart_top10,
            "overlap_top10": len(set(naive_top10) & set(smart_top10)),
        },
    }


def reading_between_lines(c: dict) -> list[dict]:
    """Snippets from career substance that matched JD concepts WITHOUT relying on the skills list."""
    text = F.substance_text(c)
    out = []
    for cat, pats in jd._CONCEPT_PATTERNS.items():
        if jd.CONCEPT_WEIGHTS.get(cat, 0) <= 0:
            continue
        snippets = []
        for p in pats:
            for m in p.finditer(text):
                lo, hi = max(0, m.start() - 45), min(len(text), m.end() + 45)
                snippets.append("…" + text[lo:hi].strip() + "…")
                if len(snippets) >= 2:
                    break
            if len(snippets) >= 2:
                break
        if snippets:
            out.append({"concept": _CONCEPT_LABEL.get(cat, cat), "snippets": snippets})
    return out


def gap_analysis(c: dict, matched_concept_keys: list[str]) -> list[str]:
    """Missing JD must-have concept categories (RedRob 'gap analysis' style)."""
    matched = set(matched_concept_keys)
    return [_CONCEPT_LABEL[k] for k in MUST_HAVE_CONCEPTS if k not in matched]


def candidate_detail(c: dict) -> dict:
    """Full profile + score breakdown + reading-between-the-lines + gap analysis."""
    s = scoring.score_candidate(c)
    is_hp = honeypot.is_honeypot(c)
    return {
        **_brief(c),
        "summary": c.get("profile", {}).get("summary", ""),
        "headline": c.get("profile", {}).get("headline", ""),
        "career_history": c.get("career_history", []),
        "education": c.get("education", []),
        "skills": c.get("skills", []),
        "redrob_signals": c.get("redrob_signals", {}),
        "is_honeypot": is_hp,
        "honeypot_flags": honeypot.impossibility_flags(c) if is_hp else [],
        "score": s["score"] if not is_hp else 0.0,
        "components": s["components"],
        "modifier": s["modifier"],
        "penalties": s["penalties"],
        "concerns": s["concerns"],
        "reading_between_lines": reading_between_lines(c),
        "gaps": gap_analysis(c, s["matched_concepts"]),
        "reasoning": reasoning.build_reasoning(c, s, 1),
    }
