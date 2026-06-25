"""Encoded representation of the job description we rank against.

This is where the JD (docs/01_job_description_analysis.md) becomes machine-usable: a weighted, gated
rubric (reusing the calibration pattern in docs/07), the concept lexicon that maps plain-language
phrasing -> JD requirements (catches plain-language Tier-5s, docs/03 Trap 2), role/skill maps, and the
negative signals to penalize. Kept as data + small pure helpers so the reasoning layer can cite exactly
which JD criteria a candidate matched or missed.
"""

from __future__ import annotations

import re

# --- Experience band (JD: "5-9 years", ideal 6-8, soft outside) ---
EXPERIENCE_BAND = (5.0, 9.0)
IDEAL_EXPERIENCE = (6.0, 8.0)

# --- Location preference (JD: Pune/Noida; Tier-1 Indian cities; outside India case-by-case) ---
PREFERRED_LOCATIONS = {"pune", "noida"}
ACCEPTABLE_INDIAN_METROS = {
    "hyderabad", "mumbai", "delhi", "bangalore", "bengaluru", "gurgaon", "gurugram", "chennai", "noida", "pune",
}

# --- Services / consulting firms (JD hard-negative if career is *entirely* here) ---
SERVICES_FIRMS = {
    "tcs", "tata consultancy", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "mindtree", "hcl", "tech mahindra", "ltimindtree", "mphasis",
    "deloitte", "ibm", "dxc", "larsen", "persistent",
}

# --- Role relevance: keyword in title -> base relevance (engineering-role plausibility gate). ---
#     Non-engineering titles score near zero so "Marketing Manager with 9 AI skills" sinks (Trap 1).
ROLE_RELEVANCE = {
    # core AI/ML/IR roles
    "ai engineer": 1.0, "ml engineer": 1.0, "machine learning": 1.0, "applied scientist": 1.0,
    "research scientist": 0.85, "data scientist": 0.85, "nlp": 1.0, "research engineer": 0.9,
    "search engineer": 1.0, "relevance engineer": 1.0, "recommendation": 1.0,
    # strong adjacent engineering
    "backend engineer": 0.7, "data engineer": 0.72, "analytics engineer": 0.66, "software engineer": 0.66,
    "full stack": 0.55, "platform engineer": 0.6, "staff engineer": 0.7, "principal engineer": 0.7,
    "machine learning engineer": 1.0,
    # other engineering (capable but off-domain)
    "cloud engineer": 0.42, "devops": 0.4, "sre": 0.42, "frontend": 0.38, "mobile": 0.36,
    "qa engineer": 0.3, "java developer": 0.45, ".net": 0.42, "data analyst": 0.5,
}
DEFAULT_ROLE_RELEVANCE = 0.06  # non-engineering titles (HR/Sales/Marketing/Accountant/etc.)

# --- Skills the JD actually values (matched against skill names; depth gated by role). ---
RELEVANT_SKILLS = {
    "nlp", "natural language processing", "information retrieval", "embeddings", "embedding",
    "sentence-transformers", "sbert", "bert", "transformers", "semantic search", "vector search",
    "faiss", "pinecone", "weaviate", "qdrant", "milvus", "elasticsearch", "opensearch", "bm25",
    "ranking", "learning to rank", "recommendation systems", "recommender", "information retrieval",
    "pytorch", "tensorflow", "python", "machine learning", "deep learning", "mlops", "mlflow",
    "fine-tuning llms", "lora", "rag", "llm", "xgboost", "scikit-learn", "spark", "airflow",
}

# --- Concept lexicon: JD requirement -> plain-language signals to look for in *career descriptions*.
#     The weight reflects how decisive the concept is for THIS role. (Trap 2 defense.) ---
CONCEPT_LEXICON: dict[str, list[str]] = {
    "embeddings_retrieval": [
        "embedding", "embeddings", "semantic search", "vector search", "retrieval", "nearest neighbor",
        "sentence-transformers", "sentence transformer", "bge", "e5", "faiss", "dense retrieval",
    ],
    "vector_db_hybrid_search": [
        "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "vector database",
        "hybrid search", "bm25",
    ],
    "ranking_recsys": [
        "ranking", "rank", "recommendation", "recommender", "search relevance", "learning to rank",
        "personalization", "personalisation", "matching system", "relevance",
    ],
    "ranking_eval": [
        "ndcg", "mrr", "mean average precision", "a/b test", "ab test", "offline evaluation",
        "online metric", "click-through", "ctr", "evaluation framework",
    ],
    "ml_production": [
        "production", "deployed", "real users", "at scale", "pipeline", "inference", "serving", "latency",
    ],
    "nlp_ir": ["nlp", "natural language", "information retrieval", "text classification", "language model"],
    "llm": ["llm", "large language model", "fine-tune", "fine-tuning", "rag", "retrieval-augmented"],
    # CV/speech/robotics-only is a JD negative (down-weight if this dominates and NLP/IR is absent).
    "cv_speech_robotics": [
        "image classification", "computer vision", "object detection", "speech recognition", "tts",
        "text-to-speech", "robotics", "autonomous", "image segmentation",
    ],
}

# Weight per concept category for the relevance component (sums are normalized at use time).
CONCEPT_WEIGHTS = {
    "embeddings_retrieval": 1.0,
    "vector_db_hybrid_search": 0.9,
    "ranking_recsys": 1.0,
    "ranking_eval": 0.8,
    "ml_production": 0.6,
    "nlp_ir": 0.7,
    "llm": 0.4,
    "cv_speech_robotics": 0.0,  # not credited (negative handled separately)
}

# --- Disqualifier / down-weight concepts (JD "explicitly do NOT want"). ---
NEGATIVE_CONCEPTS = {
    "title_chaser": "frequent <1.5yr job hops climbing the title ladder",
    "framework_enthusiast": "langchain-tutorial / demo-only AI exposure",
    "services_only": "entire career at consulting/services firms",
    "cv_speech_only": "primary expertise CV/speech/robotics without NLP/IR",
    "research_only": "pure research, no production deployment",
    "recent_llm_only": "AI experience only recent (<12mo) LangChain+OpenAI, no pre-LLM ML",
    "stale_no_prod_code": "senior with no production code in 18 months",
}

# Component weights for the final relevance score (sum to 1.0). Provisional; tuned in Slice 3.
COMPONENT_WEIGHTS = {
    "relevance": 0.30,     # concept coverage in career substance (semantic-ish; embeddings augment in Slice 2)
    "title_career": 0.28,  # engineering-role plausibility + product-vs-services
    "experience": 0.12,    # 5-9 band fit
    "skill_depth": 0.20,   # depth of relevant skills, gated by role
    "education": 0.10,
}
BEHAVIORAL_MODIFIER_RANGE = (0.5, 1.15)  # bounded so availability modulates, never overrides relevance


# --- precompiled concept matchers ------------------------------------------------

def _compile(terms: list[str]) -> list[re.Pattern]:
    return [re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE) for t in terms]


_CONCEPT_PATTERNS = {cat: _compile(terms) for cat, terms in CONCEPT_LEXICON.items()}


def concept_hits(text: str) -> dict[str, int]:
    """Count matches per concept category in `text` (already-lowercased text is fine)."""
    hits: dict[str, int] = {}
    for cat, pats in _CONCEPT_PATTERNS.items():
        c = 0
        for p in pats:
            c += len(p.findall(text))
        if c:
            hits[cat] = c
    return hits


def role_relevance(title: str) -> float:
    """Map a job title to engineering-role relevance in [0,1] (longest keyword match wins)."""
    t = (title or "").lower()
    best = DEFAULT_ROLE_RELEVANCE
    best_len = 0
    for kw, val in ROLE_RELEVANCE.items():
        if kw in t and len(kw) > best_len:
            best, best_len = val, len(kw)
    return best


def jd_query_text() -> str:
    """Canonical JD query string for semantic matching (Slice 2 embeddings)."""
    return (
        "Senior AI engineer for a product company building production embeddings-based retrieval, "
        "semantic search, ranking and recommendation systems at scale. Strong Python. Vector databases "
        "and hybrid search (FAISS, Elasticsearch, Pinecone). Designing evaluation frameworks for ranking "
        "(NDCG, MRR, MAP, A/B testing). NLP and information retrieval. LLM fine-tuning and RAG. "
        "Shipped end-to-end search/ranking/recommendation to real users."
    )
