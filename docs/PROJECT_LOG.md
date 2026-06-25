# Project Log — Redrob Candidate Ranking Challenge

Chronological journal of decisions, experiments, results, and next steps. Newest entries at the bottom.
Kept in sync with git history (small, frequent commits) — this doubles as the iteration audit trail the
challenge grades at Stage 4.

---

## 2026-06-25 — Phase 0: Project setup

**Goal:** Understand the challenge end-to-end and stand up a persistent, auditable project.

**Done:**
- Read the full bundle: `Track 01 ... .md`, the four `.docx` (job description, README, submission spec,
  redrob signals), `candidate_schema.json`, `validate_submission.py`, `sample_submission.csv`,
  `sample_candidates.json`, `submission_metadata_template.yaml`.
- Ran a full-pool scan of `candidates.jsonl` (100,000 records) for distributions and trap signatures.
- Wrote `docs/00`–`docs/05` capturing challenge, JD analysis, dataset/signals, traps/honeypots,
  scoring/submission spec, and the approach/roadmap.
- Scaffolded `src/` (data_loader, jd_profile, honeypot, features, scoring, reasoning, rank) as documented
  stubs; added `requirements.txt`, `.gitignore`, `submission_metadata.yaml`, root `README.md`.
- Initialized git; large data bundle is git-ignored.

**Key facts established (so we never re-derive them):**
- Task: rank **top-100** of **100k** candidates for a **Senior AI Engineer** JD → CSV
  `candidate_id,rank,score,reasoning`.
- Scoring: **0.50·NDCG@10 + 0.30·NDCG@50 + 0.15·MAP + 0.05·P@10** on hidden ground truth. **Top-10 dominates.**
- Pool reality: only **~722 AI-titled** candidates; bulk are non-tech (~5,800 each Business Analyst/HR/etc.).
  75% India; mean YOE 7.2; recruiter_response_rate mean 0.44.
- Traps: keyword stuffers, **plain-language Tier-5s** (no buzzwords — the candidates that win NDCG),
  behavioral twins, **~80 honeypots** (>10% in top-100 = DQ). Verified 21 candidates with expert@0-month
  skills — honeypot signatures are machine-detectable.
- Hard limits: ranking step **≤5 min, ≤16 GB, CPU-only, no network**. Git history + defend-interview graded.

**Decisions:**
- Architecture = **hybrid explainable pipeline** (honeypot filter → JD gates/penalties → semantic + structured
  scoring → behavioral multiplier → reasoning). No per-candidate LLM calls; embeddings precomputed offline.
- Substance over keywords; behavioral signals as a **bounded multiplier** (0.5–1.15×), not an override.
- Validate locally via archetype probes + manual top-50 audit (no leaderboard feedback exists).
- Initial component weights set in `src/scoring.py` (semantic .30 / title_career .30 / skill_depth .18 /
  experience .12 / education .10) — provisional, to be justified as tuned.

**Next steps (Phase 1):**
- Implement `data_loader.iter_candidates` + `candidate_text_blob`; decide streaming vs full materialization
  within 16 GB. Then Phase 2: `honeypot.py` checks, calibrate to flag ~80 with no false positives.

---

## 2026-06-25 — Literature survey + prior-work review

**Goal:** Ground the design in published methods and salvage reusable assets from a prior project (`old/`).

**Done:**
- Reviewed `old/`: `visualCalibrationReport.html` is a reusable **role-calibration rubric** pattern
  (capability map + weighted/gated rubric + evidence-confidence model). Documented in `docs/07`. Other old/
  files (mock-interview spec, entitlements notes, xlsx/png) are not relevant.
- Ran a deep-research literature survey (5 angles, 23 sources, 99 claims → 25 verified → **21 confirmed,
  4 refuted**). Wrote `docs/06_literature_survey.md` with citations; folded decisions into `docs/05`.

**Key validated decisions (see docs/06):**
- **Retrieve-and-rerank** architecture confirmed (SBERT). Our pipeline shape is correct.
- **Precomputed bi-encoder embeddings + cosine** for 100k-scale CPU matching; default embedder
  **all-MiniLM-L6-v2 (384-d)**, also benchmark BGE/E5/GTE-small.
- **Embeddings alone are a weak resume↔JD signal** (conSultantBERT) → keep the structured/rules layer; rely on
  modern instruction-tuned embedders + good query/text construction (we can't fine-tune: no labels/time).
- **No LTR, no LLM at inference** — we have no relevance labels and no click logs; LLM explanation layers
  aren't verifiably faithful. Use **unsupervised RRF (k≈60) + a white-box weighted utility** (JobMatchAI
  design, Cormack RRF). Refuted: "RRF beats weighted fusion" → choose fusion empirically.
- **JD hand-encoded as a gated rubric** (docs/07), not NER (NER only ~72% F).
- **Evaluate** on a hand-built archetype relevance set (NDCG@k/MAP/P@k) + manual top-50 audit.

**Literature GAPS = our original contributions (interview talking points):**
- Adversarial/honeypot/keyword-stuffer detection — no reliable source → our rule-based consistency filter.
- Must/nice-to-have rubric modeling — not evidenced → our calibration rubric (docs/07).
- Faithful non-LLM explanations — only candidate approach was refuted → our templated-from-facts reasoning.

**Caution:** JobMatchAI's benchmark numbers and "LLM can't hallucinate a ranking" guarantee were refuted —
cite its *design*, not its results.

**Next steps:** unchanged — Phase 1 (data loader) then Phase 2 (honeypot filter). Embedder benchmarking lands
in Phase 4; fusion (RRF vs weighted) settled on archetypes in Phase 4/8.

---

## 2026-06-25 — Added CLAUDE.md (session bootstrap)

**Done:** Wrote `CLAUDE.md` at repo root — the agent operating guide so any fresh session recovers full context
by reading `docs/` (00–07) for understanding and this `PROJECT_LOG.md` for state. It encodes the
non-negotiable rules (CPU/offline/5-min, 0 honeypots in top-100, top-10 obsession, no-hallucination reasoning),
the repo map, data location, commands, and the working conventions (log every step, commit incrementally).

**Convention reminder for future sessions:** after each meaningful step, append a PROJECT_LOG entry and commit
in small increments; update `docs/` (and `CLAUDE.md`) when decisions change.

**Next steps:** begin Phase 1 — implement `data_loader.iter_candidates` + `candidate_text_blob`.

---

## 2026-06-25 — Slice 1 complete: baseline ranker produces a valid CSV

**Goal:** End-to-end baseline ranker (rules + lexical, no embeddings) → first valid, honeypot-free submission.

**Done:**
- `jd_profile.py` — JD encoded as role-relevance map, relevant-skill set, weighted concept lexicon
  (matchers precompiled), component weights, and a `jd_query_text()` for Slice 2.
- `features.py` — extractors: title/career plausibility, product-vs-services, concept evidence in
  *substance text* (career descriptions, NOT skills list — stuffer defense), experience-band fit,
  relevant-skill depth (proficiency×endorsement×duration, assessment-corroborated), education, location, tenure.
- `scoring.py` — weighted components + skill-depth gated by role + soft penalties (services-only,
  CV/speech-only, title-chaser, location) × bounded behavioral modifier (0.5–1.15). Returns full breakdown.
- `reasoning.py` — fact-grounded, rank-banded, varied templated rationales with honest concerns.
- `rank.py` — streaming pipeline + top-K heap; honeypots filtered from contention.

**Results (full 100k run):**
- Runtime **156s** (< 5-min budget); **65 honeypots filtered**; `validate_submission.py` **passes**.
- **Top-10 are all genuine AI/ML/Search/Recsys engineers** at product companies (Amazon, Zomato, CRED,
  Razorpay, Paytm, Microsoft, Sarvam), 6–8 yrs, India — zero stuffers/honeypots/non-eng titles.
- Massive improvement over the naive `sample_submission` (which ranked HR Managers #1).

**Notes / Slice-3 backlog:**
- Concept-regex over 100k texts is the runtime cost (~156s). Optimize (combined patterns) for margin.
- Top candidates with no concerns share an identical closer ("Strong on both relevance and availability") —
  add more variation for the Stage-4 variation check.
- Genpact not in SERVICES_FIRMS; revisit services list.

**Next steps:** build the demo UI (Part B/C/D of the plan) — FastAPI backend wrapping the ranker, then the
Vite/React core wow-set, deployed as the HF sandbox. Slice 2 (embeddings) and Slice 3 (tuning) follow.

---

## 2026-06-25 — Demo UI built (FastAPI + Vite/React core wow-set)

**Goal:** A SOTA, jury-impressing demo that doubles as the mandatory sandbox. (User decisions: ranker-first,
Vite+React, optional LLM layer, core wow-set now + maximal backlog.) See `docs/08_demo_ui.md`.

**Done:**
- **Backend** (`app/`): FastAPI wrapping `src/`. Endpoints `/api/rank` (ranked + honeypot flags + naive-vs-smart
  comparison), `/api/jd` (capability rubric), `/api/candidate/{id}` (breakdown + reading-between-the-lines +
  gap analysis), `/api/stats`, optional `/api/explain` (LLM, demo-only, key-gated, graceful fallback).
  Curated 80-candidate demo sample committed (30 top + 15 stuffers + 10 honeypots + 25 random).
- **Frontend** (`frontend/`): Vite + React 19 + TS + Tailwind 4 + TanStack Query + Recharts + Framer Motion.
  Five core panels (JD Intelligence, ranked leaderboard w/ score rings, candidate drawer w/ radar +
  reading-between-the-lines + gaps, guardrail strip, naive-vs-smart stats) + optional AI-narration button.
- **Deploy** (`Dockerfile`, `.dockerignore`): multi-stage (build UI → FastAPI serves dist + API on $PORT) →
  one HF Docker Space URL; `docker run` fallback. Deploy steps documented (run by user; Docker/HF CLI absent here).
- Verified end-to-end via uvicorn: `/` serves the React app, `/api/rank` returns the real ranking
  (top-3 = recsys/ML/search engineers), 10 honeypots flagged, **top-10 overlap with keyword ranker = 3/10**.

**Decisions / notes:**
- Bundle ~681 KB (recharts+framer) — fine for a demo; could code-split later.
- LLM narration uses a fact-only prompt and never affects ranks; off by default (no key) so the "100% offline
  ranking" story stays clean.

**Backlog (maximal showcase — docs/08):** gap-analysis upgrade, naive↔smart toggle animation, pipeline viz,
pool analytics, upload-your-own-sample, Slice-2 semantic sub-score surfacing.

**Next steps:** user deploys the HF Space (fill `submission_metadata.sandbox_link`); then Slice 2 (precomputed
embeddings) → Slice 3 (tuning), which flow through the UI automatically.

---

## 2026-06-25 — Tooling: uv + just (no pip)

**Done (per user request):** standardized on **uv** (no pip anywhere) and added a cross-platform **`justfile`**
(works on Windows PowerShell & Linux/macOS sh) as the professional task interface.
- `justfile` recipes: `install`, `rank`, `validate`, `check`, `api`, `web`, `build-web`, `serve`,
  `docker-build`, `docker-run` (all Python steps go through `uv run`/`uv pip`).
- Dockerfile uses the official `uv` binary + `uv pip install --system` (no pip).
- README/CLAUDE.md/docs/08/metadata updated to the `just` + `uv` workflow; `reproduce_command` = `just rank`.
- Verified: `just --list` and `just validate` (→ "Submission is valid") run via `uv run`.

**Next steps:** unchanged — deploy sandbox, then Slice 2 (embeddings).
