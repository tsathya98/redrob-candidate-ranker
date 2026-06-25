# 06 — Literature Survey

A multi-source, adversarially-verified survey of how to build candidate-to-JD matching/ranking systems,
mapped to *our* constraints (CPU-only, offline, ≤5 min, ~100k pool, no per-candidate LLM calls, no labels).

> Method: 5 search angles → 23 sources fetched → 99 candidate claims → top 25 verified by 3-vote adversarial
> check → **21 confirmed, 4 refuted**. Confirmed claims below carry citations; refuted ones are called out so
> we don't build on them. Full machine output archived in the tool-results transcript.

## TL;DR — what the literature endorses (and how we'll use it)

1. **Retrieve-and-rerank is the canonical architecture.** First stage retrieves a candidate set cheaply
   (hybrid lexical + dense); a heavier re-ranker re-scores only the top ~100–1000. This is exactly our
   pipeline shape (docs/05) and the reason it fits the compute budget. ✅ validated.
2. **Bi-encoder embeddings, precomputed offline, + cosine** is what makes large-pool matching CPU-friendly —
   embed once, compare cheaply. Use a modern small instruction-tuned embedder. ✅ validated.
3. **Embeddings alone are a weak matching signal** for resumes↔JDs (they *complement*, not paraphrase). →
   our **hybrid (embeddings + lexical + structured rules)** design is the right call, not pure semantic search.
4. **With no labels, use unsupervised fusion (RRF) + a white-box weighted utility** — both training-free and
   explainable. Learning-to-rank needs labels/click-logs we don't have → correctly deferred.
5. **Big gaps in the literature** (adversarial-profile detection, must/nice-to-have rubrics, faithful
   non-LLM explanations) → these become *our original contributions*, justified below.

---

## Confirmed findings (with citations)

### A. Architecture: retrieve-and-rerank  ·  confidence: HIGH
A first-stage retriever fetches ~100 candidates; a **cross-encoder** re-ranks them, "substantially improving
final results" via joint query–document attention. Cross-encoders are too slow to score millions of pairs, so
they're used **only** as a re-ranker. — *SBERT docs (retrieve & re-rank).*
→ **For us:** retrieve with a cheap hybrid scorer over all 100k, then apply the expensive components only to a
shortlist. A cross-encoder is optional (CPU cost); a white-box re-ranker (below) is the safer default.

### B. Embeddings: bi-encoders, precomputed, but domain matters  ·  confidence: HIGH
Unsupervised cosine over vanilla BERT/TF-IDF is weak (ROC-AUC ~0.53–0.57); a domain-fine-tuned Siamese SBERT
("conSultantBERT") reached **0.85** — because "word overlap or semantic similarity … is not a sufficiently
strong signal for identifying which resumes match a given vacancy." The bi-encoder is chosen precisely because
precomputed embeddings scale one vacancy against a large resume pool. — *Lavi et al., arXiv:2109.06501.*
→ **For us:** (1) embeddings are necessary but **not sufficient** — keep the structured/rules layer on top;
(2) we can't fine-tune (no labels/time), so lean on **modern instruction-tuned embedders** (E5 / BGE / GTE /
all-MiniLM) which are far stronger zero-shot than the 2021 vanilla-BERT baseline this paper critiques;
(3) invest in **good query/text construction** (JD query text; candidate text blob) to close the gap.

### C. Concrete production stack: JobMatchAI  ·  confidence: HIGH (design only)
Hybrid retrieval = BM25 (Elasticsearch, k=150) + ANN over **all-MiniLM-L6-v2 384-d** embeddings (k=150) +
skill knowledge-graph traversal (k=75), merged via **RRF (k=60)**. Re-rank = a **fully white-box weighted
utility** over 6 interpretable factors: *skill 0.35, experience 0.25, location 0.15, salary 0.10, semantic
0.10, company fit 0.05*; skill match = Jaccard + KG-relatedness bonus; **no learned parameters beyond the
embeddings.** — *Vyas et al., arXiv:2603.14558.*
→ **For us:** strong template for an **explainable, label-free re-ranker** and a proven lightweight embedder
(all-MiniLM-L6-v2). ⚠️ **Cite the design, not the numbers** — its NDCG@10/latency benchmark and its
"LLM cannot hallucinate a ranking" guarantee were **REFUTED** in verification (see below).

### D. Score fusion: RRF is a solid unsupervised baseline  ·  confidence: HIGH
`RRF(d) = Σ_r 1/(k + rank_r(d))`, with **k≈60**, no training required — "unsupervised methods are attractive
because they require no training examples." — *Cormack et al., SIGIR 2009.*
→ **For us:** RRF fuses the semantic and lexical rankings with zero labels. ⚠️ Do **not** assume RRF beats
weighted/linear fusion — that claim (and "RRF beats Condorcet/CombMNZ") was **REFUTED (0-3)**. Pick fusion
empirically; a weighted utility (C) and RRF are both legitimate, and we may use both at different stages.

### E. Learning-to-rank needs labels we don't have  ·  confidence: HIGH
XGBoost `rank:ndcg` implements LambdaMART (also `rank:map`, `rank:pairwise`) — CPU-friendly. — *XGBoost docs.*
Label-free is possible only via **biased implicit feedback** (clicks): position bias must be corrected with
inverse-propensity weighting / counterfactual ERM (Propensity-Weighted RankSVM; XGBoost
`lambdarank_unbiased`). — *Joachims et al., WSDM 2017 (arXiv:1608.04468).*
→ **For us:** we have **neither relevance labels nor click logs** (cold-start, single hidden-GT scoring). So
LTR is correctly **out of scope** for the submission; unsupervised RRF + white-box utility is the right base.
(LTR is a "future, if engagement logs existed" note — good to mention at the Stage-5 interview.)

### F. JD skill extraction  ·  confidence: HIGH (modest accuracy)
Transformer-ensemble NER extracts technical/non-technical skills from JDs at ~**72% / 67% F-score**, beating
CRF/hybrid baselines. — *NLP Journal 2024 (ScienceDirect S2949719124000505).*
→ **For us:** our JD is **fixed and known**, so we **hand-encode** it as a calibration rubric (docs/07) rather
than auto-extract — higher precision than 72% NER and fully under our control. NER is overkill here.

### G. Offline evaluation  ·  confidence: HIGH (needs some judgments)
Use **NDCG@k, MAP, MRR@k, P@k**; SBERT ships a `CrossEncoderRerankingEvaluator` computing MAP/MRR@k/NDCG@k. —
*SBERT docs.* All require *some* relevance judgments.
→ **For us:** the hidden GT uses exactly these metrics (docs/04). With no GT locally, we build a small
**hand-labeled archetype/relevance set** (a few dozen clear good/bad/honeypot candidates) and compute NDCG/MAP
on it as a regression check — plus the manual top-50 audit (docs/05).

---

## Refuted / cautioned claims (do NOT build on these)

| Claim | Verdict | Implication |
|-------|---------|-------------|
| JobMatchAI hits NDCG@10 0.81 / <82 ms / 7% over BM25 | REFUTED 1-2 | use its *architecture*, ignore its *numbers* |
| Separating scoring from a generative-explanation LLM means it "cannot hallucinate a ranking" | REFUTED 1-2 | LLM explanation layers are **not** guaranteed faithful → we avoid LLMs in reasoning entirely |
| RRF beats Condorcet/CombMNZ | REFUTED 0-3 | RRF is *a* good fusion, not *the best* — choose empirically |
| RRF beats weighted/linear score fusion | REFUTED 0-3 | weighted utility (our component scoring) is equally legitimate |

---

## Gaps the literature did NOT cover → our original contributions

The adversarial verification surfaced **no reliable sources** for several parts of our problem. These are
where our system differentiates (and good interview talking points):

1. **Adversarial / low-quality profile detection** (keyword stuffing, fabricated or internally inconsistent
   resumes, **honeypots**). No surviving claim addressed this. → Our **rule-based impossibility/consistency
   filter** (docs/03, `honeypot.py`) is our own design — and the literature gap confirms it's genuinely novel
   and necessary, not reinventing a known wheel.
2. **Must-have vs nice-to-have requirement modeling & role-fit rubrics** from a JD. Not evidenced. → Filled by
   the **weighted, gated calibration rubric** reused from prior work (docs/07).
3. **Faithful, non-hallucinated explanations without per-candidate LLM calls.** The only candidate approach was
   refuted. → Our **strictly-templated-from-real-facts reasoning** (`reasoning.py`, no LLM) is the safe,
   verifiable choice and directly satisfies the Stage-4 "no hallucination" check.

## Bias & pitfalls (flagged in the question; treat as caveats)

Automated resume ranking carries documented bias/fairness risks (*arXiv:2507.11548*; *PNAS Nexus
pgaf089, 2025*). Features like location, education tier, and company prestige can encode bias.
→ **For us:** the GT is synthetic (fairness stakes are lower here), and the JD's negatives (services-only,
research-only, etc.) are *role-fit*, not protected attributes. Still, we **prefer soft down-weighting over hard
exclusion** wherever a signal is a proxy, and we keep every score component explainable so any bias is visible
and defensible.

---

## Decisions locked in for our build (folded into docs/05)

- **Architecture = hybrid retrieve → white-box weighted re-rank.** Confirmed by A, C, D.
- **Embedder = a small modern instruction-tuned model** (candidate: all-MiniLM-L6-v2 384-d as the proven
  lightweight baseline; consider BGE-small/E5-small), **precomputed offline**, cosine at rank time. (A, B, C)
- **Fusion:** combine semantic + lexical via RRF *and/or* weighted utility — decide empirically on archetypes;
  no assumption that one dominates. (D, refutations)
- **No LTR, no LLM at inference** — no labels, no click logs, faithfulness/compute risks. (E, refutations)
- **JD encoded by hand as a gated rubric** (docs/07), not NER. (F)
- **Honeypot/consistency filter and templated reasoning are our own** — literature confirms these are gaps. (gaps)
- **Evaluate** on a hand-built archetype relevance set with NDCG@k/MAP/P@k + manual audit. (G)

## Sources (verified-claim backbone)

- SBERT — Retrieve & Re-Rank: https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html *(primary)*
- conSultantBERT, Lavi et al. 2021: https://arxiv.org/pdf/2109.06501 *(primary)*
- JobMatchAI, Vyas et al. 2026 (design only; numbers refuted): https://arxiv.org/pdf/2603.14558 *(primary)*
- Reciprocal Rank Fusion, Cormack et al. SIGIR 2009: https://dl.acm.org/doi/10.1145/1571941.1572114 *(primary)*
- XGBoost Learning-to-Rank: https://xgboost.readthedocs.io/en/stable/tutorials/learning_to_rank.html *(primary)*
- Unbiased LTR / counterfactual, Joachims et al. WSDM 2017: https://arxiv.org/abs/1608.04468 *(primary)*
- Skill-extraction ensemble NER, NLP Journal 2024: https://www.sciencedirect.com/science/article/pii/S2949719124000505 *(primary)*
- SBERT CrossEncoderRerankingEvaluator: https://sbert.net/docs/package_reference/cross_encoder/evaluation.html *(primary)*
- Bias in automated ranking: https://arxiv.org/pdf/2507.11548 ; https://academic.oup.com/pnasnexus/article/4/3/pgaf089/8071848 *(primary)*

## Open questions carried forward

- Best CPU-only embedder vs the 5-min/16 GB budget at 100k (precompute mitigates; benchmark in Phase 4).
- Exact fusion choice (RRF vs weighted) — settle empirically on the archetype set (Phase 4/8).
- Calibrating the honeypot filter to flag ~80 with zero false positives (Phase 2).
