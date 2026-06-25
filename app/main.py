"""FastAPI app — serves the ranking API and (in production) the built React UI.

Run dev:  uvicorn app.main:app --reload --port 8000
The scored ranking is fully offline. The optional /api/explain endpoint is the ONLY part that may call an
LLM; it is clearly demo-only, never affects ranks, and degrades gracefully when no API key is set.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import ranker_service as svc

ROOT = Path(__file__).resolve().parent.parent
DEMO_PATH = ROOT / "app" / "demo_data" / "demo_candidates.jsonl"
FRONTEND_DIST = ROOT / "frontend" / "dist"

app = FastAPI(title="Redrob Candidate Ranker — Demo API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Load + rank the demo sample once at startup (cached).
_CANDIDATES = svc.load_candidates(DEMO_PATH)
_BY_ID = {c["candidate_id"]: c for c in _CANDIDATES}
_RANKING = svc.rank_candidates(_CANDIDATES)


class RankRequest(BaseModel):
    candidates: list[dict] | None = None


class ExplainRequest(BaseModel):
    candidate_id: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "demo_candidates": len(_CANDIDATES), "llm_enabled": _llm_enabled()}


@app.get("/api/jd")
def jd_rubric() -> dict:
    return svc.JD_RUBRIC


@app.get("/api/candidates")
def list_candidates() -> dict:
    return {"candidates": [svc._brief(c) for c in _CANDIDATES]}


@app.post("/api/rank")
def rank(req: RankRequest) -> dict:
    if req.candidates:
        if len(req.candidates) > 200:
            raise HTTPException(400, "Demo accepts at most 200 candidates.")
        return svc.rank_candidates(req.candidates)
    return _RANKING


@app.get("/api/stats")
def stats() -> dict:
    return _RANKING["stats"]


@app.get("/api/candidate/{candidate_id}")
def candidate(candidate_id: str) -> dict:
    c = _BY_ID.get(candidate_id)
    if c is None:
        raise HTTPException(404, f"Unknown candidate_id {candidate_id}")
    return svc.candidate_detail(c)


# --- optional LLM narration (demo-only; never affects ranking) ---

def _llm_enabled() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


@app.post("/api/explain")
def explain(req: ExplainRequest) -> dict:
    """Narrate a candidate's fit using ONLY the deterministic score facts. Demo-only flourish."""
    if not _llm_enabled():
        raise HTTPException(503, "LLM narration disabled (no ANTHROPIC_API_KEY set). Ranking is unaffected.")
    c = _BY_ID.get(req.candidate_id)
    if c is None:
        raise HTTPException(404, f"Unknown candidate_id {req.candidate_id}")

    detail = svc.candidate_detail(c)
    facts = {
        "title": detail["title"], "years_experience": detail["yoe"], "company": detail["company"],
        "score_components": detail["components"], "matched_evidence": detail["reading_between_lines"],
        "gaps": detail["gaps"], "concerns": detail["concerns"],
    }
    try:
        import anthropic
        client = anthropic.Anthropic()
        model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
        msg = client.messages.create(
            model=model,
            max_tokens=300,
            system=("You are a recruiting analyst. Explain in 3-4 sentences why this candidate fits a Senior "
                    "AI Engineer role, using ONLY the provided facts. Do not invent skills or employers. "
                    "Be specific and acknowledge any gaps/concerns honestly."),
            messages=[{"role": "user", "content": f"Candidate facts (JSON):\n{facts}"}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        return {"candidate_id": req.candidate_id, "model": model, "explanation": text, "demo_only": True}
    except Exception as e:  # noqa: BLE001 - surface any LLM error without breaking the demo
        raise HTTPException(502, f"LLM call failed: {e}")


# --- serve the built React app in production (mounted last so /api/* wins) ---
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/")
    def _root() -> dict:
        return {"message": "Frontend not built. Run `npm run build` in frontend/, or use the API at /api/*."}
