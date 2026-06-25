# 01 — Job Description Analysis

The role we rank against. **Decoded into scoring criteria.** Source: `job_description.docx`.

## The role at a glance

- **Title:** Senior AI Engineer — **Founding Team**, Redrob AI (Series A, AI-native talent-intelligence platform).
- **Location:** Pune / Noida (hybrid, flexible). Open to relocation from **Tier-1 Indian cities**
  (Hyderabad, Pune, Mumbai, Delhi NCR explicitly welcomed). Outside India: case-by-case, **no visa sponsorship**.
- **Experience:** 5–9 years (a *range, not a hard cutoff* — strong signals outside the band still considered).
- **Mandate:** own the intelligence layer — ranking/retrieval/matching. First 90 days: audit current
  BM25+rules system → ship a v2 (embeddings, hybrid retrieval, LLM re-ranking) → build eval infra
  (offline benchmarks, A/B, recruiter-feedback loops). Then drive long-term architecture and mentor hires.

## The ideal candidate (the JD spells this out)

- ~**6–8 yrs** total, of which **4–5 in applied ML/AI at product companies** (not pure services).
- Has **shipped ≥1 end-to-end ranking / search / recommendation system to real users at meaningful scale**.
- Strong, defensible opinions on **retrieval (hybrid vs dense)**, **evaluation (offline vs online)**, and
  **LLM integration (fine-tune vs prompt)** — grounded in systems they actually built.
- In or willing to relocate to **Noida/Pune**.
- **Active on the platform** / clearly in the job market (so recruiters can reach them).

> The JD says outright: *"We're not expecting to find many matches in a 100K pool... we'd rather see 10 great
> matches than 1000 maybes."* → reinforces the **top-10-is-everything** strategy.

## MUST-HAVE (positive signals — high weight)

| Requirement | What to detect in profiles |
|-------------|----------------------------|
| Production **embeddings-based retrieval** (sentence-transformers, OpenAI emb, BGE, E5, …) | career descriptions mentioning embeddings, semantic/vector search, retrieval in prod |
| Production **vector DB / hybrid search** (Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS) | named infra in career history/skills |
| **Strong Python** | Python skill + code-quality signals |
| **Ranking-eval frameworks** (NDCG, MRR, MAP, offline→online correlation, A/B) | mentions of ranking metrics, A/B testing, eval design |
| Shipped **search/ranking/recsys end-to-end at scale**, at a **product company** | career descriptions of recsys/search shipped to users |

## NICE-TO-HAVE (small positive weight, never a gate)

LLM fine-tuning (LoRA/QLoRA/PEFT); learning-to-rank (XGBoost/neural); HR-tech/recruiting/marketplace
domain; distributed systems / large-scale inference; open-source AI/ML contributions.

## HARD NEGATIVES — "explicitly do NOT want" (strong down-weight / near-disqualify)

| Negative | Detectable signature |
|----------|----------------------|
| **Title-chasers** | job-hopping every ~1.5 yr to climb Senior→Staff→Principal; short tenures across many companies |
| **Framework enthusiasts** | profile/GitHub dominated by LangChain tutorials / "how I built a demo with [hot framework]" |
| **Consulting/services-only careers** | *entire* career at TCS / Infosys / Wipro / Accenture / Cognizant / Capgemini (and similar). NOTE: prior product-company experience cancels this. |
| **CV / speech / robotics primary** without NLP/IR | skills/career centered on image classification, speech recognition, TTS, robotics, no NLP/retrieval |
| **Closed-source-only 5+ yrs** with no external validation | no papers/talks/open-source; opaque proprietary-only work |

## DISQUALIFIERS the JD "actually applies"

- **Pure-research-only** (academic/research labs) with **no production deployment**.
- **AI experience = recent (<12 mo) LangChain-calling-OpenAI only**, *unless* substantial pre-LLM-era ML
  production experience exists. (They want people who understood retrieval/ranking "before it was fashionable".)
- **Senior who hasn't written production code in 18 months** (moved to pure "architecture"/"tech-lead").

## Logistics → soft scoring factors

- **Notice period:** sub-30-day ideal (can buy out ≤30 days); 30+ still in scope but bar rises.
  → use `redrob_signals.notice_period_days` as a mild factor.
- **Location/relocation:** Noida/Pune-located or `willing_to_relocate` from a Tier-1 Indian city scores higher;
  outside India is a soft negative (no visa sponsorship).

## The explicit participant note (the crux — quoted intent)

> "The right answer is NOT 'find candidates whose skills section contains the most AI keywords.' That's a
> trap we've explicitly built in. The right answer involves reasoning about the gap between what the JD says
> and what it means. A Tier-5 candidate may not use 'RAG' or 'Pinecone' but if their career history shows they
> built a recommendation system at a product company, they're a fit. A candidate who has all the AI keywords as
> skills but whose title is 'Marketing Manager' is not a fit. ... Also weigh behavioral signals — a
> perfect-on-paper candidate who hasn't logged in for 6 months with a 5% response rate is not actually
> available. Down-weight them appropriately."

### How we translate this into ranking logic

1. **Career evidence > skill keywords.** Score what the *career descriptions* show they built (recsys/search/
   ranking at product companies), not the length of the skills array.
2. **Title/role plausibility gate.** AI skills on a non-engineering title (Marketing Manager, HR Manager,
   Accountant) are near-worthless — treat as keyword stuffing.
3. **Skill *depth* not *count*** — weight by `proficiency × endorsements × duration_months`, not raw presence.
4. **Behavioral availability is a multiplier**, not a tiebreaker (see `02_dataset_and_signals.md`).
5. **NLP/IR alignment over CV/speech** — penalize profiles whose AI gravity is image/speech/robotics.

> Concrete pool example: `CAND_0000001` (Ira Vora) — Backend/Data Engineer at **Mindtree (services)** in
> **Toronto**, AI skills weighted toward **Speech Recognition / TTS / Image Classification**. Looks "AI" but
> hits *three* soft-negatives (services-only, outside India, CV/speech focus, transitioning-not-shipped).
> A keyword ranker over-rates them; our system should not.
