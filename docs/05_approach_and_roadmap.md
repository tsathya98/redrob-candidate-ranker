# 05 — Approach & Roadmap

How we turn the understanding in `00`–`04` into a working, explainable, CPU-only ranker — and the phased plan
to build it.

## Design principles (derived from the docs)

1. **Substance over keywords** — score what career descriptions *show*, not skill-array length.
2. **Top-10 obsession** — NDCG@10 is half the score; get the top-10 set *and order* right.
3. **Never ship a honeypot / never trust a stuffer** — hard consistency + plausibility gates.
4. **Availability is a multiplier** — behavioral signals modulate, never dominate, relevance.
5. **Explainable end-to-end** — every score decomposes into named components feeding the reasoning text.
6. **Offline-heavy, online-cheap** — precompute embeddings/indexes; `rank.py` stays within 5 min CPU/no-net.

## Architecture — hybrid explainable pipeline (no per-candidate LLM calls)

```
candidates.jsonl
   │
   ▼  data_loader.py        stream-parse JSONL, normalize fields, build candidate text blob
   │
   ▼  honeypot.py           impossibility checks → flag & force-bottom (Trap 4)
   │
   ▼  jd_profile.py         encoded JD: must-haves, negatives, ideal profile, concept lexicon
   │
   ▼  features.py + scoring.py
   │     ├─ Component A: Semantic relevance  (embeddings: career text vs JD query) + BM25 lexical
   │     │     → catches plain-language Tier-5s (Trap 2)
   │     ├─ Component B: Title/career fit    (engineering role? recsys/search/ranking evidence? product co?)
   │     │     → defeats keyword stuffers (Trap 1)
   │     ├─ Component C: Experience-band fit  (5–9 yrs sweet spot, soft outside)
   │     ├─ Component D: Skill depth          (proficiency × endorsements × duration, corroborated by
   │     │                                     skill_assessment_scores) — not raw keyword count
   │     ├─ Component E: Education/cert prior  (mild)
   │     ├─ JD hard-gates / soft-penalties    (services-only, pure-research, recent-LLM-only, title-chaser,
   │     │                                     CV/speech-only, location/relocation)
   │     └─ Behavioral modifier (×)           (response rate, last_active recency, open_to_work,
   │                                           interview_completion, saved_by_recruiters, notice) — Trap 3
   │
   ▼  combine → final score → sort (desc, tie-break candidate_id asc) → top 100
   │
   ▼  reasoning.py          per-candidate 1–2 sentence rationale: real facts + JD link + honest concern
   │
   ▼  rank.py --candidates ... --out submission.csv   (single reproduce command)
```

### Why hybrid (embeddings + lexical + structured + rules)

- **Embeddings** find Tier-5s who phrase things plainly (semantic match on career descriptions).
- **Lexical/BM25** keeps precise term matches (named infra: FAISS, Pinecone, etc.).
- **Structured features + rules** encode the JD's explicit positives/negatives that no embedding captures
  (product-vs-services, experience band, title plausibility, location).
- **Behavioral modifier** encodes "actually hireable."
- All are CPU-friendly and offline once embeddings are precomputed.

### Candidate model selection (to firm up in build)

- Embedding model: a small CPU-friendly sentence-transformer (e.g. **BGE-small / E5-small / all-MiniLM**),
  precomputed offline, vectors cached to disk; `rank.py` loads cached vectors (no model inference per run if
  the JD is fixed — embed the JD once and dot-product against cached candidate vectors).
- Optional learning-to-rank later (XGBoost) **only if** we can construct a trustworthy proxy label set —
  otherwise stay rule-/score-based (safer with no ground-truth feedback).

## Phased roadmap

| Phase | Goal | Output |
|------|------|--------|
| **0 — Setup (this step)** | Docs, scaffold, git, project log | `docs/`, `src/` stubs, repo, `PROJECT_LOG.md` |
| **1 — Data + EDA** | Robust loader; profile the pool; quantify traps/honeypots | `data_loader.py`, EDA notes in log |
| **2 — Honeypot filter** | Implement & validate impossibility checks; confirm ~80 flagged | `honeypot.py` + assert 0 in top-100 |
| **3 — JD profile + structured scoring** | Encode JD, build components B–E + gates/penalties | `jd_profile.py`, `features.py`, `scoring.py` |
| **4 — Semantic layer** | Precompute embeddings; add Component A + BM25; fuse | embedding artifact + fusion in `scoring.py` |
| **5 — Behavioral modifier** | Implement availability multiplier; handle behavioral twins | modifier in `scoring.py` |
| **6 — Reasoning generation** | Fact-grounded, varied, rank-consistent rationales | `reasoning.py` |
| **7 — End-to-end + validate** | Produce CSV; pass validator; honeypot gate; time the run | `submission.csv`, timing report |
| **8 — Local quality assessment** | Build a defensible offline eval (no ground truth) — sanity-rank known good/bad archetypes, manual top-50 audit | eval notes |
| **9 — Sandbox + metadata + repo polish** | HF Space/Streamlit demo, fill metadata, README, final repo | sandbox link, `submission_metadata.yaml` |

## Validating without a leaderboard

Since there's no feedback signal, we trust **methodology and manual audit**:
- Construct **archetype probes** (a perfect Tier-5, an obvious stuffer, a honeypot, a behavioral-twin pair) and
  assert the ranker orders them correctly.
- **Manually audit our top-50** every iteration — does each belong? any stuffer/honeypot/CV-only leaked in?
- Track **honeypot count in top-100** (must be 0) and the **share of top-100 that are genuine eng/product fits**.
- Keep changes small and logged so we can attribute quality shifts to specific decisions.

## Open questions to revisit during build

- Exact weighting of the 5 components + modifier (start hand-set, justify each in the log).
- Embedding model choice vs the 5-min/16 GB budget at 100k scale (precompute mitigates).
- How aggressively to gate non-India candidates (JD: outside-India case-by-case, no visa) vs relocation flag.
- Whether any learning-to-rank adds value without reliable labels (default: skip unless clearly justified).
