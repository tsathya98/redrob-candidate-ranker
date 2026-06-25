# Redrob Intelligent Candidate Discovery — Ranking Engine

Our submission for the **Hack2Skill × RedRob Data & AI Challenge (Track 01)**: rank the top-100 best-fit
candidates from a 100,000-candidate pool for the *Senior AI Engineer (Founding Team)* job description —
reasoning about contextual + behavioral fit, not keyword overlap.

> **Status:** Phase 0 — project setup complete (docs, scaffold, git). Ranking pipeline is being built in
> phases; see `docs/05_approach_and_roadmap.md`.

## Data setup

The challenge bundle is **not** included in this repo (large + provided separately). Place it in `data/`:

```
data/
  candidates.jsonl          # the 100k pool
  validate_submission.py    # format validator
  candidate_schema.json, sample_candidates.json, sample_submission.csv, *.docx, ...
```

`data/` and `old/` are git-ignored.

## Reproduce the submission (target interface)

```bash
python src/rank.py --candidates data/candidates.jsonl --out submission.csv
python data/validate_submission.py submission.csv
```

The ranking step runs **CPU-only, offline, ≤5 min, ≤16 GB** (embeddings precomputed offline). See
`docs/04_scoring_and_submission.md` for full constraints.

## Approach (one paragraph)

A **hybrid, explainable, CPU-only pipeline**: a honeypot/impossibility filter, JD-encoded hard-gates and
soft-penalties, semantic relevance (precomputed embeddings + BM25 over career-description text — to catch
strong candidates who don't use buzzwords), structured feature scoring (title/career evidence, experience
band, skill *depth*, education), and a bounded behavioral-availability multiplier from the 23 Redrob signals.
Reasoning strings are templated from real profile facts, so they cannot hallucinate. Full rationale in `docs/`.

## Repository layout

```
docs/                     Challenge understanding + design (read 00 -> 05)
  00_challenge_overview.md
  01_job_description_analysis.md
  02_dataset_and_signals.md
  03_traps_and_honeypots.md
  04_scoring_and_submission.md
  05_approach_and_roadmap.md
  PROJECT_LOG.md          Chronological project journal (decisions, experiments, results)
src/                      Ranking package (data_loader, jd_profile, honeypot, features, scoring, reasoning, rank)
requirements.txt          Dependencies (CPU-only, offline)
submission_metadata.yaml  Portal metadata (mirrors submission spec)
```

## Documentation

Start with `docs/00_challenge_overview.md`. The running log of what we've done and decided lives in
`docs/PROJECT_LOG.md`.
