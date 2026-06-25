# CLAUDE.md — Agent Operating Guide

> **You (the agent) are working on the Hack2Skill × RedRob "Intelligent Candidate Discovery & Ranking"
> challenge.** This file is your entry point. Read it fully, then bootstrap context from `docs/` before doing
> anything else. It is written so that a brand-new session — with zero prior memory — can pick up exactly
> where the last one left off.

## 🚀 Start every session here (bootstrap, in order)

1. **Read `docs/PROJECT_LOG.md` FIRST.** It is the chronological source of truth for *what has happened, what
   was decided, and what's next*. The newest entry at the bottom is the current state. Trust it over any
   assumption.
2. **Skim the docs in order** for understanding (each is one concern, scannable):
   - `docs/00_challenge_overview.md` — what the challenge is, the 5-stage eval pipeline, strategy.
   - `docs/01_job_description_analysis.md` — the JD decoded into scoring criteria (must/nice/negatives).
   - `docs/02_dataset_and_signals.md` — candidate schema + the 23 behavioral signals + pool distributions.
   - `docs/03_traps_and_honeypots.md` — the 4 trap classes + honeypot DQ rule + detection strategies.
   - `docs/04_scoring_and_submission.md` — exact CSV/validator rules, metric weights, reasoning rubric, limits.
   - `docs/05_approach_and_roadmap.md` — the architecture + the **phased build plan** (find the current phase).
   - `docs/06_literature_survey.md` — cited, verified methods that justify the design.
   - `docs/07_reusable_prior_work.md` — the role-calibration rubric pattern reused from `old/`.
3. **Check `git log --oneline`** to see recent work, then `git status` for any in-flight changes.
4. **Resume from the "Next steps" in the latest `PROJECT_LOG.md` entry** (cross-check against `docs/05`'s phase
   table).

> If `docs/` and this file ever disagree, `docs/` (and the latest `PROJECT_LOG.md` entry) win — update this file.

## 🎯 What we're building (one paragraph)

A ranker that takes one fixed job description (*Senior AI Engineer, Founding Team @ Redrob AI*) and the 100,000-
candidate pool, and outputs the **top-100 best-fit candidates** as a CSV (`candidate_id,rank,score,reasoning`).
"Best fit" = deep contextual + behavioral fit, **not** keyword overlap. Approach = a **hybrid, explainable,
CPU-only pipeline**: honeypot/consistency filter → JD-encoded gates/penalties → semantic (precomputed
embeddings + lexical) + structured scoring → bounded behavioral multiplier → fact-grounded reasoning.

## 🚫 Non-negotiable rules (violating these loses the competition)

1. **The ranking step must run CPU-only, offline (NO network/LLM API calls), ≤5 min, ≤16 GB.** Embeddings/
   indexes are precomputed *offline*; `rank.py` only loads cached artifacts. Never add a hosted-LLM call to the
   ranking path. (docs/04)
2. **Honeypot rate in top-100 must be 0** (>10% = hard disqualification). Run the honeypot/consistency filter
   and assert zero before any submission. (docs/03)
3. **Top-10 dominates the score** (NDCG@10 = 0.50 weight). Spend disproportionate care on the top-10 set *and*
   their order. (docs/04)
4. **Reasoning must be fact-grounded — NEVER hallucinate.** Every claim in a `reasoning` cell must correspond
   to a real value in that candidate's profile. Use templated-from-data generation, no LLM. Be specific, tie to
   the JD, and state honest concerns. (docs/04 §reasoning, docs/06 gaps)
5. **Substance over keywords.** Score what `career_history[].description` shows the candidate built; gate
   AI-skill credit on genuine engineering roles. The bundled `sample_submission.csv` deliberately fails this —
   don't imitate it. (docs/01, docs/03)
6. **Output must pass `validate_submission.py` exactly** (100 rows, ranks 1–100 once, scores non-increasing,
   tie-break by candidate_id ascending). (docs/04)
7. **Max 3 submissions, no leaderboard feedback.** Validate locally; don't "probe". (docs/00)

## 🧭 How to work in this repo

- **Pick up the current phase** from the latest `PROJECT_LOG.md` entry and the `docs/05` phase table. Do the
  next phase; don't jump ahead.
- **Keep the project flow persistent — this is a hard requirement from the user:**
  - After any meaningful step, **append an entry to `docs/PROJECT_LOG.md`** (date, goal, done, decisions,
    results, next steps). This is how a future session recovers context.
  - **Commit in small, logical increments** with clear messages. The challenge grades *real git iteration*
    (Stage 4) and penalizes flat/single-dump history. End commit messages with the Co-Authored-By trailer.
  - If a decision changes the design, update the relevant `docs/` file too (not just the log).
- **Reuse before you write.** The `src/` modules are stubbed with phase-tagged `TODO`s; implement those rather
  than inventing parallel structures. Reuse the calibration-rubric pattern (docs/07) for JD encoding/scoring.
- **Match existing style** in `src/` (type hints, module docstrings that reference the docs, pure functions).
- **Update `submission_metadata.yaml`** as facts firm up (python version, precompute time, methodology).

## 🗂️ Repo map

```
CLAUDE.md                 ← you are here (agent bootstrap guide)
README.md                 human-facing project readme
docs/                     understanding + design (read 00→07) + PROJECT_LOG.md (state of the project)
src/                      ranking package (implement the phase-tagged TODOs):
  data_loader.py          stream/parse candidates.jsonl, build candidate text blob   [Phase 1]
  jd_profile.py           JD encoded as a gated rubric + concept lexicon             [Phase 3]
  honeypot.py             impossibility/consistency checks (force honeypots down)    [Phase 2]
  features.py             per-candidate feature extraction                           [Phase 3/5]
  scoring.py              component scores + behavioral modifier + final ranking     [Phase 3-7]
  reasoning.py            fact-grounded, varied, rank-consistent rationale strings   [Phase 6]
  rank.py                 CLI entry: the single reproduce command (BUILT, Slice 1)    [Phase 1-7]
app/                      FastAPI demo backend (wraps src/) + demo_data sample          [UI]
  main.py, ranker_service.py, demo_data/demo_candidates.jsonl, requirements.txt
frontend/                 Vite+React+TS demo UI (the sandbox) — see docs/08            [UI]
Dockerfile, .dockerignore single-image deploy (HF Docker Space / docker run)
requirements.txt          ranker deps (CPU-only, offline; ranker is stdlib-only)
submission_metadata.yaml  portal metadata (fill TODOs before submission)
```

> **Status note (keep current):** Slice 1 ranker is BUILT (`rank.py` produces a valid, honeypot-free
> top-100 in ~156s). The demo UI (FastAPI `app/` + Vite `frontend/`) is BUILT and verified via uvicorn.
> Next: deploy the HF sandbox, then Slice 2 (precomputed embeddings) → Slice 3 (tuning). See `docs/08` + log.

## 📦 Where the data lives (`data/` — NOT in git; ~465 MB, git-ignored)

The challenge bundle is provided separately; place it in **`data/`** (the whole directory is git-ignored).
A fresh clone has no `data/` — drop the bundle there before running anything.

```
data/
  candidates.jsonl              100,000 candidates (the pool to rank)
  sample_candidates.json        first 50, pretty-printed (quick schema inspection)
  candidate_schema.json         JSON Schema for a candidate record
  validate_submission.py        the format validator — run before every submission
  sample_submission.csv         format reference ONLY (deliberately low quality)
  job_description.docx           the JD (already decoded in docs/01)
  submission_spec.docx           rules/metrics/limits (already captured in docs/04)
  redrob_signals_doc.docx        the 23 signals (already captured in docs/02)
  submission_metadata_template.yaml
```
`old/` holds a separate prior project (also git-ignored); only `visualCalibrationReport.html` was relevant
(distilled into docs/07).

## 🛠️ Commands you'll use

```bash
# Sanity-check the CLI (already wired)
python src/rank.py --help

# Validate a submission (run before every upload)
python data/validate_submission.py submission.csv

# The single reproduce command (the ranking pipeline is built across phases 1-7)
python src/rank.py --candidates data/candidates.jsonl --out submission.csv

# Inspect the pool quickly (streaming; the file is large)
wc -l data/candidates.jsonl

# Demo UI (the sandbox): backend + frontend (see docs/08)
pip install -r app/requirements.txt && uvicorn app.main:app --port 8000
cd frontend && npm install && npm run dev          # http://localhost:5173 (proxies /api)
```

## ✅ Pre-submission release gate (see docs/04 for the full checklist)

`validate_submission.py` passes · exactly 100 rows · all candidate_ids exist · **0 honeypots in top-100** ·
reasonings factual/JD-connected/honest/varied/rank-consistent · `rank.py` timed ≤5 min CPU/offline · repo
reproducible from clean checkout · metadata YAML filled · sandbox link live.

---

*Keep this file current. When the architecture, phase, or conventions change, update CLAUDE.md and `docs/` so
the next session starts from the truth.*
