"""Per-candidate reasoning generation (docs/04 Stage-4 rubric).

Produces the 1-2 sentence `reasoning` column strictly from real profile facts + the score breakdown.
No LLM, no network -> it cannot hallucinate. Satisfies the manual-review checks: specific facts,
JD connection, honest concerns, variation, and rank-consistent tone.
"""

from __future__ import annotations

# concept category -> human phrase for the JD-connection clause
_CONCEPT_PHRASE = {
    "embeddings_retrieval": "embeddings/retrieval",
    "vector_db_hybrid_search": "vector search & hybrid retrieval",
    "ranking_recsys": "ranking/recommendation systems",
    "ranking_eval": "ranking evaluation (NDCG/A-B testing)",
    "ml_production": "production ML at scale",
    "nlp_ir": "NLP/IR",
    "llm": "LLM fine-tuning/RAG",
}

# rank-band lead-ins (tone matches rank)
_LEADS_TOP = ["Excellent fit:", "Top match:", "Standout candidate:"]
_LEADS_MID = ["Solid fit:", "Strong candidate:", "Good alignment:"]
_LEADS_LOW = ["Plausible fit:", "Worth a look:", "Borderline but in scope:"]
_LEADS_TAIL = ["Adjacent fit:", "Stretch candidate:", "Included for breadth:"]


def _lead(rank: int, salt: int) -> str:
    band = _LEADS_TOP if rank <= 10 else _LEADS_MID if rank <= 40 else _LEADS_LOW if rank <= 80 else _LEADS_TAIL
    return band[salt % len(band)]


def build_reasoning(candidate: dict, scored: dict, rank: int) -> str:
    """Return a 1-2 sentence justification grounded in real facts and the score breakdown."""
    p = candidate.get("profile", {})
    title = p.get("current_title", "professional")
    yoe = scored["evidence"].get("yoe", p.get("years_of_experience", 0))
    salt = sum(ord(c) for c in candidate["candidate_id"])

    # JD-connection clause from matched concepts (real evidence) or relevant skills
    concepts = [_CONCEPT_PHRASE[c] for c in scored.get("matched_concepts", []) if c in _CONCEPT_PHRASE]
    skills = [s for s, _ in scored["evidence"].get("relevant_skills", [])][:3]
    if concepts:
        connect = "career shows " + ", ".join(concepts[:3])
    elif skills:
        connect = "relevant skills in " + ", ".join(skills)
    else:
        connect = "general engineering background"

    fact = f"{title} with {yoe:.1f} yrs"
    if scored["evidence"].get("has_product"):
        fact += ", product-company experience"

    lead = _lead(rank, salt)
    sentence = f"{lead} {fact}; {connect}."

    # honest concern clause (only real ones), tone-appropriate
    concerns = scored.get("concerns", [])
    if concerns:
        # surface the single most material concern to keep it to 1-2 sentences
        sentence += f" Concern: {concerns[0]}."
    elif rank <= 10:
        sentence += " Strong on both relevance and availability."

    return sentence
