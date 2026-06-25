# 03 — Traps & Honeypots

The dataset is **adversarial by design**. The README and JD name four trap classes plus ~80 honeypots.
Mishandling them is the difference between a top submission and disqualification. This file catalogs each
trap and a concrete, *profile-logic* detection strategy (no special-casing of specific IDs — the spec says a
good system should avoid them naturally).

## Why this matters

- **NDCG@10 = 0.50** of the score → a single trap in the top-10 is very costly.
- **Honeypot rate > 10% in top-100 = hard disqualification** at Stage 3 (regardless of composite score).
- Falling for traps is read as "the system isn't reading profiles, just embedding keywords."

---

## Trap 1 — Keyword stuffers

**What:** Profiles with a perfect-looking AI skills list but a career/title that has nothing to do with the
role. The bundled `sample_submission.csv` *deliberately* ranks these #1 (e.g. "HR Manager with 9 AI core
skills" at rank 1) to show the naive failure mode.

**Detect:**
- **Title/role plausibility:** `current_title` and `career_history[].title` are non-engineering
  (Marketing Manager, HR Manager, Accountant, Sales Executive, Content Writer, …) → AI skills are noise.
- **Career-evidence gap:** `career_history[].description` never shows building ML/search/ranking/retrieval
  systems, despite AI skills being listed.
- **Skill vs assessment mismatch:** high self-reported `proficiency` but low `skill_assessment_scores`.
- **Shallow skills:** AI skills with low `endorsements` and/or low `duration_months` (listed, not used).

**Handle:** Score career evidence, not skill-array length. Gate AI-skill credit on engineering titles/roles.

---

## Trap 2 — Plain-language "Tier-5s" (the *most valuable* candidates)

**What:** Genuinely excellent fits who **don't use the buzzwords**. They built a recommendation/search/ranking
system at a product company but their profile says it in plain English — never "RAG", "Pinecone", "embeddings".
Pure keyword/embedding matching **misses** them; finding them is how you win NDCG@10.

**Detect:**
- Career descriptions describing the *substance*: "built a recommendation system", "search relevance",
  "ranking model", "semantic matching", "personalization", "information retrieval", "A/B tested ranking",
  even without the trendy nouns.
- Product-company employer + engineering title + scale language ("real users", "production", "at scale").
- Strong `skill_assessment_scores` corroborating real ability even when the skills list is modest.

**Handle:** Semantic similarity over **full career-description text** (not just skills), plus a concept-level
lexicon that maps plain phrasing → JD requirements. This is the core reason we use embeddings, not just BM25.

---

## Trap 3 — Behavioral twins

**What:** Two candidates with near-identical static profiles but different **behavioral signals** — one is
active/responsive/available, the other stale/unresponsive/unavailable. The ground truth rewards the actually-
hireable one.

**Detect / handle:** This is exactly what the behavioral modifier is for (`02_…`): when relevance is tied,
`recruiter_response_rate`, `last_active_date` recency, `open_to_work_flag`, `interview_completion_rate`,
`saved_by_recruiters_30d`, and `notice_period_days` separate the twins. Make the modifier strong enough to
split otherwise-identical pairs but not so strong it overrides real relevance differences.

---

## Trap 4 — Honeypots (~80, forced to relevance tier 0) — **DQ risk**

**What:** Profiles with **logically impossible** internals. The spec's examples:
- "8 years of experience at a company founded 3 years ago"
- "'expert' proficiency in 10 skills with 0 years used"

**Detectable impossibility checks (rule-based, exact — these are the safety net):**

| Check | Rule |
|-------|------|
| Tenure vs timeline | `duration_months` inconsistent with `start_date`/`end_date` span; or sum of tenures ≫ plausible given `years_of_experience` |
| Experience vs age of career | total career span / YOE contradicts company-founding plausibility |
| Expert@0 | skill `proficiency == "expert"` (or advanced) with `duration_months == 0` |
| Proficiency vs assessment | "expert" self-rating with a near-zero `skill_assessment_scores` entry |
| Date sanity | `start_date > end_date`; `is_current` true but `end_date` set; education `start_year > end_year` |
| Overlap impossibility | many simultaneous full-time current roles; overlapping tenures summing past the timeline |
| Round-number / template artifacts | implausibly uniform fabricated values |

> **Verified already:** a full-pool scan found **21 candidates with ≥1 expert-proficiency skill at 0 months
> duration** — confirming this signature is real and machine-detectable. (Honeypots use a *combination* of
> impossibilities; we'll tune thresholds so we flag the ~80 without nuking legitimate profiles.)

**Handle:** A dedicated `honeypot.py` filter computes an impossibility score; anything flagged is **forced to
the bottom** (relevance 0 / excluded from top-100). Keep a count and assert **honeypot rate in our top-100 = 0**
as a release gate before any submission.

---

## Cross-cutting principle

Every trap defends the same thesis: **read the profile, reason about substance, and weigh availability.**
- Keyword stuffers → *substance over keywords.*
- Plain-language Tier-5s → *substance over keywords* (the other direction).
- Behavioral twins → *availability matters.*
- Honeypots → *internal consistency matters.*

Our pipeline order (honeypot filter → JD gates/penalties → semantic + structured scoring → behavioral
modifier) is built to handle all four. See `05_approach_and_roadmap.md`.
