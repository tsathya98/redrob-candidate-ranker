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
