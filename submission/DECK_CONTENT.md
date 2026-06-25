# Idea Submission Deck — copy-paste content

Paste each block into the matching slide of `Idea Submission Template _ Redrob.pptx`. Keep it tight on
the slide (bullets), put the prose in speaker notes. `TODO` = only you have it. Grounded in `docs/` —
nothing here is invented.

---

## Slide 1 — Title
- **Team Name:** TODO
- **Problem Statement:** Intelligent Candidate Discovery & Ranking — from a 100,000-profile pool, return
  the **top-100 best-fit candidates** for the *Senior AI Engineer (Founding Team) @ Redrob AI* JD, judging
  **contextual + behavioral fit, not keyword overlap**, under a **CPU-only, offline, ≤5-min** budget.
- **Team Leader Name:** TODO

---

## Slide 2 — Solution Overview
**What is your solution?**
- A **hybrid, explainable, CPU-only ranking engine**: honeypot filter → JD-encoded gated rubric → semantic
  (embeddings) + lexical relevance → **cross-encoder rerank** → bounded behavioral multiplier → fact-grounded
  reasoning. One command produces the ranked CSV.

**What differentiates it from traditional candidate matching?**
- **Substance over keywords:** we score what a candidate *built* (career-history descriptions), and **exclude
  the skills list from relevance** — so keyword-stuffers don't rank.
- **Reads profiles, not just text:** an **impossibility/honeypot filter** forces logically-impossible profiles
  out (0 in our top-100 vs the >10% that disqualifies).
- **Availability-aware:** a bounded **behavioral multiplier** down-weights perfect-on-paper-but-unreachable
  candidates (stale logins, low recruiter-response).
- **Compliant & fast by design:** heavy models run **offline** (the JD is fixed → precompute once, cache to
  JSON); the scored step is **stdlib, CPU-only, offline, ~190s**.

---

## Slide 3 — JD Understanding & Candidate Evaluation
**Key requirements extracted from the JD** (see `docs/01`, `docs/jd_text.md`):
- Must: production **embeddings retrieval**, **vector/hybrid search**, strong **Python**, **ranking
  evaluation** (NDCG/MRR/MAP/A-B).
- Profile shape: **5–9 yrs** (ideal 6–8), **product company** (not pure services/research), shipped an
  **end-to-end ranking/search/recsys** system, Pune/Noida or willing to relocate, **active** on platform.
- Explicit negatives: services-only, CV/speech-without-NLP, title-chasers, recent-LLM-only/framework demos.

**Most important signals & fit beyond keywords:**
- Career-description **evidence** of retrieval/ranking work; **engineering-role plausibility gate**
  (a "Marketing Manager" with 9 AI skills scores ~0).
- **Skill depth** (proficiency × endorsements/duration, corroborated by Redrob assessment scores) — not raw
  skill count.
- **Behavioral availability** from the 23 Redrob signals.
- Plain-language fit caught by **semantic embeddings** (a Tier-5 who built a recsys without buzzwords still ranks).

---

## Slide 4 — Ranking Methodology
**Retrieve → score → rerank:**
1. **Recall funnel:** fast structured score over all 100k → keep a top pool.
2. **Semantic relevance:** `bge-small-en-v1.5` bi-encoder, cosine to a **distilled JD query** (provenance:
   `docs/jd_text.md`), blended 50/50 with lexical concept matching.
3. **Cross-encoder rerank:** `bge-reranker-v2-m3` takes half-authority over the top tier (drives NDCG@10).
4. **Structured components** (weighted): relevance .30, title/career .28, skill-depth .20, experience .12,
   education .10.
5. **Multipliers:** soft penalties (services-only ×0.45, CV/speech ×0.6, title-chaser ×0.85, location) ×
   **bounded behavioral modifier** (0.5–1.15).

**Final:** `score = fit × penalties × behavioral`; sort desc, tie-break by candidate_id (matches the
validator). Models run **offline**; `rank.py` reads cached JSON → CPU/offline.

---

## Slide 5 — Explainability & Data Validation
**How decisions are explained:**
- Every candidate carries a **component breakdown** + **relevance parts** (lexical / semantic / cross-encoder),
  surfaced in the demo UI and in a **1–2 sentence reasoning** string per candidate.

**No hallucinations:**
- Reasoning is **templated strictly from real profile facts** (titles, employers, YoE, named skills, signal
  values) — **no LLM in the output path**, so a claim can't reference something not in the profile. Honest
  concerns (notice period, low response rate) are stated, and tone is rank-consistent.

**Suspicious / low-quality profiles:**
- **Honeypot/impossibility filter** (e.g., expert skill with 0 months used, duration > career span) forces
  them out — **calibrated to 65 genuinely-impossible profiles with 0 false positives**; **0 reach our top-100**.

---

## Slide 6 — End-to-End Workflow
`JD (fixed)` → **[offline precompute, GPU ok]** embed pool + cross-encoder rerank → cache `artifacts/*.json`
→ **[scored step: rank.py, CPU/offline ≤5min]** stream 100k → honeypot filter → component scoring +
behavioral multiplier → top-100 heap → **fact-grounded reasoning** → `submission.csv` → `validate_submission.py`.
*(diagram: `docs/05_approach_and_roadmap.md`)*

---

## Slide 7 — System Architecture
- **`src/`** ranker: `data_loader` (streaming) · `jd_profile` (gated rubric + distilled query) · `honeypot` ·
  `features` · `scoring` (semantic⊕lexical ⊕ rerank ⊕ behavioral) · `reasoning` · `rank.py` (CLI).
- **`scripts/precompute.py`** — offline, GPU: embeddings + cross-encoder → JSON artifacts.
- **Demo:** `app/` (FastAPI) + `frontend/` (Vite + React + Tailwind) → single Docker image (HF Space).
- **Compliance boundary:** GPU/transformers only in *precompute*; `rank.py` is **stdlib, CPU, offline**.
  *(architecture diagram: `docs/05`)*

---

## Slide 8 — Results & Performance
- **Validator:** passes (100 rows, ranks 1–100, scores non-increasing, tie-break by id).
- **Honeypots in top-100: 0** (the hard >10% disqualifier — cleared).
- **Runtime:** `rank.py` **~190s, CPU-only, offline, <16 GB** (precompute is the only GPU step, offline).
- **Quality (proxy, no GT):** top-100 → **83/100 in-band**, **97/100 show ranking work**, only **1 junior**,
  **92/100 available**; top-10 are senior product-company retrieval/ranking/NLP engineers (Meta, Apple,
  Netflix, Zomato, Paytm, Razorpay…), 5.9–7.9 yrs.
- **Rigor:** chose the semantic query via a **3-way ablation** and chose which JD negatives to implement via a
  **full-100k calibration** — details in `docs/09_results_and_observations.md`.

---

## Slide 9 — Technologies Used
- **Ranker:** Python 3.13, **stdlib-only** (deliberate — guarantees CPU/offline reproducibility).
- **Offline precompute:** PyTorch + sentence-transformers; **`bge-small-en-v1.5`** (embeddings) +
  **`bge-reranker-v2-m3`** (cross-encoder) — open-source, no hosted-API (Cohere etc. excluded: network).
- **Demo:** FastAPI · Vite + React + TypeScript + Tailwind · Recharts.
- **Tooling:** **uv** (reproducible envs, no pip) · **just** (cross-platform tasks) · Docker (HF Space).
- *Why:* every choice keeps the scored path inside the compute budget while letting heavy models run offline.

---

## Slide 10 — Submission Assets
- **GitHub:** TODO (repo URL) — code, docs, single reproduce command (`just rank`).
- **Sandbox/demo:** TODO (HF Space URL) — runs the ranker on a small sample end-to-end.
- **Ranked output:** `submission.csv` (top-100).
- **Docs:** `README.md`, `docs/00–09`, `docs/PROJECT_LOG.md` (iteration trail).
- **Demo video:** TODO (optional walkthrough).

---

## Slide 11 — (closing / Q&A)
- "We'd rather surface **10 great matches than 1000 maybes**" — the JD's words, and our design goal.
- Thank you / contact: TODO
