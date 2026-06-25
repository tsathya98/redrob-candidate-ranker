# Job Description (verbatim source) — Senior AI Engineer, Founding Team @ Redrob AI

> Provenance: extracted verbatim from the challenge bundle's `data/job_description.docx`.
> This file is the committed, human-readable source of truth for the JD we rank against, so the
> semantic query in `src/jd_profile.py::jd_query_text()` is provably derived from the dataset's own
> JD (not paraphrased). The structured rubric (gates/penalties/weights) in `jd_profile.py` is the
> *interpretation* of this text — see docs/01_job_description_analysis.md.

Company: Redrob AI (Series A AI-native talent intelligence platform)
Location: Pune/Noida, India (Hybrid — flexible cadence) | Open to relocation candidates from Tier-1 Indian cities
Employment Type: Full-time
Experience Required: 5–9 years (see "what we mean by this" below)

## Let's be honest about this role
We're going to write this JD differently from most. We're a Series A company that just raised our round and we're building a new AI Engineering org from scratch. This is the kind of role where the JD changes every six months because the company changes every six months. So instead of pretending we have a fixed checklist, we're going to tell you what we actually need and what we've gotten wrong before.

If you've spent your career at Google or Meta and you want a well-scoped role with a defined ladder, this isn't it. If you've spent your career bouncing between early-stage startups and you want to "just code" without having to think about product or recruiter workflows or eval frameworks, this also isn't it.

We need someone who is simultaneously comfortable with two things that sound contradictory:
- Deep technical depth in modern ML systems — embeddings, retrieval, ranking, LLMs, fine-tuning.
- Scrappy product-engineering attitude — willing to ship a working ranker in a week even if the underlying ML is "obviously suboptimal," because we need to learn from real users before we know what to actually optimize for.

We need both modes available in the same person, and we'd rather you tilt slightly toward shipper than toward researcher.

## What you'd actually be doing
The high-level mandate: own the intelligence layer of Redrob's product. That means the ranking, retrieval, and matching systems that decide what recruiters see when they search for candidates and what candidates see when they search for roles.

In practical terms, your first 90 days:
- Weeks 1-3: Audit what we currently have (mostly BM25 + rule-based scoring, working but not great). Identify the 3-4 highest-leverage things to fix.
- Weeks 4-8: Ship a v2 ranking system that demonstrably improves recruiter-engagement metrics. This will involve embeddings, hybrid retrieval, and probably some LLM-based re-ranking, but the architecture is your call.
- Weeks 9-12: Set up the evaluation infrastructure — offline benchmarks, online A/B testing, recruiter-feedback loops — so we can keep improving without flying blind.

Beyond that: driving the long-term architecture of candidate-JD matching at scale, mentoring the next hires (team growing 4 → 12 engineers in the next year), working closely with the recruiter-experience PM.

## What we mean by "5-9 years"
This is a range, not a requirement. We'll seriously consider candidates outside the band if other signals are strong. That said, here are the disqualifiers we actually apply:
- If you've spent your career in pure research environments (academic labs, research-only roles) without any production deployment — we will not move forward.
- If your "AI experience" consists primarily of recent (under 12 months) projects using LangChain to call OpenAI — we will probably not move forward, unless you can demonstrate substantial pre-LLM-era ML production experience.
- If you are a senior engineer who hasn't written production code in the last 18 months because you've moved into "architecture" or "tech lead" roles — we will probably not move forward. This role writes code.

## The skills inventory
### Things you absolutely need
- Production experience with embeddings-based retrieval systems (sentence-transformers, OpenAI embeddings, BGE, E5, or similar) deployed to real users. We care that you've handled embedding drift, index refresh, retrieval-quality regression in production.
- Production experience with vector databases or hybrid search infrastructure — Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS, or similar. The operational experience matters.
- Strong Python. We care about code quality.
- Hands-on experience designing evaluation frameworks for ranking systems — NDCG, MRR, MAP, offline-to-online correlation, A/B test interpretation.

### Things we'd like you to have but won't reject you for
- LLM fine-tuning experience (LoRA, QLoRA, PEFT)
- Experience with learning-to-rank models (XGBoost-based or neural)
- Prior exposure to HR-tech, recruiting tech, or marketplace products
- Background in distributed systems or large-scale inference optimization
- Open-source contributions in the AI/ML space

### Things we explicitly do NOT want
- Title-chasers (Senior → Staff → Principal by switching companies every 1.5 years). We need someone who plans to be here 3+ years.
- Framework enthusiasts (GitHub full of LangChain tutorials; blog posts "How I used [hot framework] to build [demo]"). We need people who think about systems, not frameworks.
- People who have only worked at consulting firms (TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini, etc.) their entire career. If you have prior product-company experience, that's fine.
- People whose primary expertise is computer vision, speech, or robotics without significant NLP/IR exposure.
- People whose work has been entirely on closed-source proprietary systems for 5+ years without external validation (papers, talks, open-source).

## On location, comp, and logistics
Location: Pune/Noida-preferred but flexible. Offices in Noida and Pune. Candidates in Hyderabad, Pune, Mumbai, Delhi NCR welcome. Outside India: case-by-case, no work-visa sponsorship.
Notice period: sub-30-day preferred; up to 30 days buyable; 30+ day notice still in scope but the bar gets higher.

## How to read between the lines — the ideal candidate
- 6-8 years total experience, of which 4-5 are in applied ML/AI roles at product companies (not pure services).
- Has shipped at least one end-to-end ranking, search, or recommendation system to real users at meaningful scale.
- Has strong opinions about retrieval (hybrid vs dense), evaluation (offline vs online), and LLM integration (when to fine-tune vs prompt) — and can defend them with reference to systems they actually built.
- Located in or willing to relocate to Noida or Pune.
- Active on Redrob platform (or clear signal of being in the job market).

We're not expecting many matches in a 100K pool. We'd rather see 10 great matches than 1000 maybes.

## Note for hackathon participants (NOT part of the matching query)
The "right answer" is not "find candidates whose skills section contains the most AI keywords" — that's a trap built into the dataset. The right answer involves reasoning about the gap between what the JD says and what it means: a Tier-5 candidate who built a recommendation system at a product company is a fit even without the buzzwords; a "Marketing Manager" with a perfect AI skill list is not. Weigh behavioral signals — a perfect-on-paper candidate who hasn't logged in for 6 months with a 5% recruiter response rate is not actually available; down-weight them.
