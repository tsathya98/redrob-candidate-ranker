# 04 — Scoring & Submission Spec

Sources: `submission_spec.docx`, `validate_submission.py`, `sample_submission.csv`,
`submission_metadata_template.yaml`. This is the contract our output must satisfy exactly.

## Output CSV format

- **Filename:** `<registered_participant_id>.csv` (UTF-8, `.csv` extension).
- **Header (row 1, exact, in order):** `candidate_id,rank,score,reasoning`
- **Rows 2–101:** exactly **100** data rows.

| Column | Type | Rule |
|--------|------|------|
| `candidate_id` | string | matches `^CAND_[0-9]{7}$`, **exists in `candidates.jsonl`**, unique |
| `rank` | int | each of **1..100 exactly once** (no 0, no gaps, no dups) |
| `score` | float | **monotonically non-increasing** with rank (score@1 ≥ score@2 ≥ … ≥ score@100); ties allowed |
| `reasoning` | string | optional but **strongly recommended**; 1–2 sentences, manually reviewed |

### Tie-break rule (enforced by validator)

If two candidates have equal `score`, the one with the **smaller `candidate_id` (ascending)** must get the
better (smaller) rank. We replicate this in our sort to pass validation. Better: avoid exact ties by using a
deterministic secondary signal so ranks reflect real ordering.

## Every rule the validator enforces (`validate_submission.py`)

1. `.csv` extension; non-empty filename stem; UTF-8 encoding.
2. Header row equals `candidate_id,rank,score,reasoning` exactly.
3. Exactly 100 non-blank data rows.
4. Each row has exactly 4 columns.
5. `candidate_id` present, matches the regex, no duplicates.
6. `rank` is an integer, 1..100, no duplicates; **all of 1..100 present** (no missing).
7. `score` parses as float.
8. **Non-increasing by rank:** sorted by rank, no later score exceeds an earlier one.
9. **Tie-break:** where scores are equal, `candidate_id` must be ascending across the tied ranks.

> Run `python validate_submission.py our_submission.csv` before *every* upload. The server runs the same check
> and auto-rejects on any violation (Stage 1).

## How the hidden ground truth scores us (Stage 2)

Composite = **0.50·NDCG@10 + 0.30·NDCG@50 + 0.15·MAP + 0.05·P@10**

| Metric | Weight | Measures |
|--------|--------|----------|
| NDCG@10 | 0.50 | quality/order of our **top 10** (uses graded relevance tiers) |
| NDCG@50 | 0.30 | quality/order of our **top 50** |
| MAP | 0.15 | precision across all relevance levels |
| P@10 | 0.05 | fraction of top-10 that are "relevant" (relevance **tier 3+**) |

- Scored **once**, after submissions close, on the full hidden ground truth. No public split, no leaderboard.
- **Tiebreak between submissions:** higher P@5, then higher P@10, then earlier timestamp.

**Implication:** order within the top-10 matters enormously (NDCG is position-weighted). Spend disproportionate
care getting the top-10 ranking *and ordering* right, and ensure all top-10 are clearly tier-3+ relevant.

## Reasoning quality (Stage 4 manual review — 10 random rows sampled)

Each sampled reasoning is checked for:

| Check | What they want |
|-------|----------------|
| Specific facts | references real profile values (YOE, current title, named skills, signal values) |
| JD connection | ties to specific JD requirements, not generic praise |
| Honest concerns | acknowledges real gaps/risks for that candidate |
| No hallucination | every claim corresponds to something actually in the profile (no invented skills/employers) |
| Variation | the 10 sampled reasonings are substantively different (not templated) |
| Rank consistency | tone matches rank (no glowing rank-95 or harsh rank-5) |

**Penalized:** empty, all-identical, name-insert templates, hallucinated skills, reasoning that contradicts rank.

**Our `reasoning.py` must therefore:** pull *actual* facts per candidate, connect to specific JD criteria,
state honest concerns (e.g. "120-day notice", "services background"), vary phrasing, and scale tone to rank.

## Compute constraints (the ranking step — Stage 3 reproduction)

| Constraint | Limit |
|-----------|-------|
| Runtime | **≤ 5 min** wall-clock |
| Memory | **≤ 16 GB** RAM |
| Compute | **CPU only** (no GPU) |
| Network | **OFF** — no hosted LLM/API calls during ranking |
| Disk (intermediate) | ≤ 5 GB |

- **Precomputation is allowed** (embeddings, indexes, model weights) and may exceed 5 min, but it must be
  produced by a documented script/artifact, and the **CSV-producing `rank.py` step** must fit the budget.
- Reproduced in a sandboxed Docker container matching these limits. If it can't reproduce → DQ.

## Submission package (all required — Section 10)

1. **The CSV** (above).
2. **Portal metadata:** team name, primary contact (name/email/phone), members, **GitHub repo URL**,
   **sandbox/demo link**, AI-tools declaration, compute-env summary, optional methodology (≤200 words).
3. **Code repo:** README with single reproduce command, full source (no hidden/manual steps), precomputed
   artifacts or a script to build them, `requirements.txt`/`pyproject.toml`, and `submission_metadata.yaml` at root.
4. **Sandbox** (Section 10.5): HuggingFace Spaces / Streamlit Cloud / Replit / Colab / Docker / Binder — runs
   the ranker on ≤100 candidates end-to-end within budget. (Mandatory; or a working `docker run` recipe.)

## Pre-submission checklist (release gate)

- [ ] `validate_submission.py` passes.
- [ ] Exactly 100 rows, ranks 1..100, scores non-increasing, tie-break correct.
- [ ] Every `candidate_id` exists in `candidates.jsonl`.
- [ ] **Honeypot count in top-100 = 0.**
- [ ] Reasonings: factual, JD-connected, honest, varied, rank-consistent, no hallucination.
- [ ] `rank.py` runs ≤5 min, ≤16 GB, CPU-only, no network (timed locally).
- [ ] Repo reproducible from clean checkout; metadata YAML filled; sandbox live.
