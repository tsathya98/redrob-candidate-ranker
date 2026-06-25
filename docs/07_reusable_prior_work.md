# 07 — Reusable Prior Work (from `old/`)

Review of a separate prior project in `old/` for assets transferable to this challenge. **One artifact is
directly reusable as a design pattern**; the rest are not relevant.

## Verdict at a glance

| File | What it is | Relevance |
|------|-----------|-----------|
| `visualCalibrationReport.html` | A **role "Calibration Report"** — decomposes a job requirement into a weighted, gated capability rubric with evidence/confidence tracking | **High — reuse the methodology** |
| `AI-powered mock client interview system.docx` | Spec for an AI mock-interview chatbot (role-specific Qs, rubric scoring, feedback) | Low — only the rubric/scoring-ownership ideas overlap |
| `conversation.txt` | Notes on an entitlements dataset for a Teams bot (identity → access level) | None — different project |
| `Book 10.xlsx`, `image (1).png` | Spreadsheet + image, unrelated | None |

---

## The reusable pattern: role → weighted gated rubric (the "Calibration Report")

`visualCalibrationReport.html` (Calibration Report — Backend Engineer, Amazon) turns a raw job requirement
into a structured, scoreable role model. Its structure is exactly what our **Deep Job Understanding** +
**scoring rubric** needs. The components:

### 1. Role summary + "what success looks like"
A prose scope statement plus an explicit success definition, and crucially an explicit **"should NOT focus on"**
(out-of-scope) list. → Our JD has the same shape: must-haves, the "ideal candidate", and an explicit
"things we do NOT want" section.

### 2. Capability map (tiered)
Capabilities bucketed by enforcement strength:
- **Must-pass** (primary gate areas — the pass bar)
- **Strong evaluation** (heavily weighted but not a hard gate)
- **Support check** (secondary signals)
- **Nice-to-have** (small positive, never rejects)
- **Out-of-scope** (must NOT drive scoring)

### 3. Rubric table — the key artifact
Each capability gets: **Area · Weight (0–28) · Gate (Yes/No) · Strong signal · Weak signal**. Example rows:

| Area | Weight | Gate | Strong signal | Weak signal |
|------|-------:|:----:|---------------|-------------|
| Backend coding & problem solving | 28 | Yes | correct backend code without heavy prompting | weak coding fundamentals |
| API/service design & debugging | 24 | Yes | reasons about API semantics | poor API understanding |
| Database basics | 16 | Yes | basic access patterns | no DB basics |
| Unit testing / clean code | 12 | Yes | easily testable code | messy code |
| Ownership & follow-through | 8 | No | finishes work end-to-end | needs handholding |
| Java/Spring Boot | 1 | No | comfortable if present | not a standalone reject |
| Messaging/queues, integration testing | 0 | No | high-level awareness | not a hard gate |

### 4. Source & confidence summary
Tracks where each piece of role knowledge came from — **Manager / JD / Web role intelligence / Inferred /
System** — each with a **confidence level (high/medium/unavailable)** and an evidence count, plus a prose
"confidence take". (Even cites external job postings for "web role intelligence".)

### 5. Ambiguity resolution
Where the role spec is silent on a common signal, it surfaces the gap with a **recommended default** and
options (e.g. "treat SQL and NoSQL as interchangeable for pass/fail? — recommended: yes").

---

## How we reuse it in this challenge

The Calibration Report pattern becomes the backbone of `src/jd_profile.py` and `src/scoring.py`:

1. **Encode the JD as a weighted, gated rubric**, not ad-hoc weights. Build a table of
   `{capability, weight, gate(bool), strong_signal, weak_signal, evidence_source}` directly from the JD's
   must-have / nice-to-have / do-NOT-want sections (docs/01). This replaces the provisional flat
   `COMPONENT_WEIGHTS` with an auditable rubric.
   - **Must-pass → hard gate** (e.g. genuine engineering role + production retrieval/ranking evidence).
   - **Strong evaluation → high weight** (semantic relevance, title/career fit, skill depth).
   - **Nice-to-have → low weight** (LoRA, LTR, OSS, HR-tech domain).
   - **Out-of-scope / do-NOT-want → penalty or hard down-weight** (services-only, CV/speech-only,
     research-only, title-chaser, recent-LLM-only).

2. **Strong-signal / weak-signal columns drive two things at once:**
   - **Feature scoring** — what to look for in `career_history[].description` and skills.
   - **Reasoning generation** (`reasoning.py`) — the "strong/weak signal" phrasing is a ready-made,
     fact-grounded vocabulary for honest per-candidate rationales (and explicitly names concerns → satisfies
     the Stage-4 "honest concerns" check).

3. **Source & confidence tracking** informs **evidence weighting**: a capability demonstrated in
   `career_history` descriptions (high confidence) should outweigh the same word merely listed in `skills`
   (low confidence) — this is precisely the keyword-stuffer defense (docs/03 Trap 1).

4. **Out-of-scope discipline** ("out-of-scope items must not drive scoring") is a guardrail against rewarding
   irrelevant keyword overlap.

> Net: we already have a proven template for the JD-understanding layer. We adapt the calibration **rubric +
> confidence model** rather than inventing scoring weights from scratch. Action item folded into Phase 3 of
> `docs/05_approach_and_roadmap.md`.
