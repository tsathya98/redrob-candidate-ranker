"""Encoded representation of the job description we rank against.

This is where the JD (docs/01_job_description_analysis.md) becomes machine-usable: the must-haves,
nice-to-haves, hard negatives, ideal-profile band, and the concept lexicon that maps plain-language
phrasing -> JD requirements (the key to catching plain-language Tier-5s, docs/03 Trap 2).

Phase 3 fills these in. Kept as data (not logic) so the reasoning layer can cite which JD criteria
a candidate matched or missed.
"""

from __future__ import annotations

# --- Experience band (JD: "5-9 years", soft outside the band) ---
EXPERIENCE_BAND = (5.0, 9.0)
IDEAL_EXPERIENCE = (6.0, 8.0)

# --- Location preference (JD: Pune/Noida; Tier-1 Indian cities; outside India case-by-case) ---
PREFERRED_LOCATIONS = {"pune", "noida"}
ACCEPTABLE_INDIAN_METROS = {"hyderabad", "mumbai", "delhi", "bangalore", "gurgaon", "gurugram", "chennai"}

# --- Services / consulting firms (JD hard-negative if career is *entirely* here) ---
SERVICES_FIRMS = {
    "tcs", "tata consultancy", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "mindtree", "hcl", "tech mahindra", "ltimindtree", "mphasis",
}

# --- Concept lexicon: JD requirement -> plain-language signals to look for in career descriptions.
#     (Trap 2: Tier-5s describe the substance without the buzzwords.) Phase 3/4 populates fully. ---
CONCEPT_LEXICON: dict[str, list[str]] = {
    "embeddings_retrieval": [
        "embedding", "semantic search", "vector search", "retrieval", "nearest neighbor",
        "sentence-transformers", "bge", "e5", "faiss",
    ],
    "vector_db_hybrid_search": [
        "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss",
        "hybrid search", "bm25",
    ],
    "ranking_recsys": [
        "ranking", "recommendation", "recommender", "search relevance", "learning to rank",
        "personalization", "matching system",
    ],
    "ranking_eval": [
        "ndcg", "mrr", "map", "a/b test", "offline evaluation", "online metric", "click-through",
    ],
    # NLP/IR alignment is wanted; CV/speech/robotics-only is a negative (Trap/JD).
    "nlp_ir": ["nlp", "natural language", "information retrieval", "text"],
    "cv_speech_robotics": ["image classification", "computer vision", "speech recognition", "tts", "robotics"],
}

# --- Disqualifier / down-weight concepts (JD "explicitly do NOT want") ---
NEGATIVE_CONCEPTS = {
    "title_chaser": "frequent <1.5yr job hops climbing title ladder",
    "framework_enthusiast": "langchain-tutorial / demo-only AI exposure",
    "services_only": "entire career at consulting/services firms",
    "cv_speech_only": "primary expertise CV/speech/robotics without NLP/IR",
    "research_only": "pure research, no production deployment",
    "recent_llm_only": "AI experience only recent (<12mo) LangChain+OpenAI, no pre-LLM ML",
    "stale_no_prod_code": "senior with no production code in 18 months",
}


def jd_query_text() -> str:
    """Return the canonical JD text used to embed the query side of semantic matching.

    TODO(Phase 4): craft a focused query string emphasizing must-haves (retrieval, ranking, eval,
    product-company, NLP/IR), distinct from the full verbose JD.
    """
    raise NotImplementedError("Phase 4: define JD embedding query.")
