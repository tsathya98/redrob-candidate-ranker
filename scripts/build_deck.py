#!/usr/bin/env python3
"""Fill the organizer-provided idea-submission template with our content (preserves their design).

We fill the body text box of each slide (and the title-page fields) in place, keeping the template's
layout/branding. Content mirrors docs/09 + README. Re-run after editing CONTENT below.

  uv pip install python-pptx
  uv run python scripts/build_deck.py
  -> submission/Redrob_Idea_Submission.pptx
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.util import Emu, Inches, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn


def no_bullet(p):
    """Suppress any inherited list bullet on a paragraph (we control markers via text)."""
    pPr = p._p.get_or_add_pPr()
    for tag in ("a:buChar", "a:buAutoNum", "a:buNone"):
        for e in pPr.findall(qn(tag)):
            pPr.remove(e)
    pPr.append(pPr.makeelement(qn("a:buNone"), {}))

TEMPLATE = Path("submission/Idea Submission Template _ Redrob.pptx")
OUT = Path("submission/Redrob_Idea_Submission.pptx")

BODY = RGBColor(0x20, 0x25, 0x2B)
HEAD = RGBColor(0x0B, 0x6B, 0x66)  # teal accent
MUTE = RGBColor(0x6B, 0x72, 0x80)

# Per-slide content. Each item: ("h"|"b"|"s"|"note", text)
#   h = bold sub-header, b = bullet, s = sub-bullet (indented), note = muted italic
CONTENT = {
    2: [
        ("h", "What is your proposed solution?"),
        ("b", "A hybrid, explainable, CPU-only ranking engine: honeypot filter -> JD gated rubric -> "
              "semantic + lexical relevance -> cross-encoder rerank -> bounded behavioral multiplier -> "
              "fact-grounded reasoning. One command produces the ranked CSV."),
        ("h", "What differentiates it from traditional matching?"),
        ("b", "Substance over keywords: scores what candidates BUILT (career descriptions); the skills "
              "list is excluded from relevance, so keyword-stuffers don't rank."),
        ("b", "Reads profiles, not just text: an impossibility/honeypot filter removes logically-impossible "
              "profiles (0 in our top-100 vs the >10% that disqualifies)."),
        ("b", "Availability-aware: a bounded behavioral multiplier down-weights perfect-on-paper but "
              "unreachable candidates (stale logins, low recruiter response)."),
        ("b", "Compliant by design: heavy models run offline (the JD is fixed -> precompute once); the "
              "scored step is stdlib, CPU-only, offline, ~190s."),
    ],
    3: [
        ("h", "Key requirements extracted from the JD"),
        ("b", "Must: production embeddings retrieval, vector/hybrid search, strong Python, ranking "
              "evaluation (NDCG/MRR/MAP/A-B)."),
        ("b", "Profile: 5-9 yrs (ideal 6-8), product company (not pure services/research), shipped an "
              "end-to-end ranking/search/recsys system, Pune/Noida or willing to relocate, active on platform."),
        ("b", "Negatives: services-only, CV/speech-without-NLP, title-chasers, recent-LLM-only/framework demos."),
        ("h", "Evaluating fit beyond keyword matching"),
        ("b", "Career-description evidence of retrieval/ranking work + an engineering-role gate "
              "(a 'Marketing Manager' with 9 AI skills scores ~0)."),
        ("b", "Skill DEPTH (proficiency x endorsements/duration, corroborated by Redrob assessments), not count."),
        ("b", "Semantic embeddings catch plain-language Tier-5s; 23 Redrob signals weigh real availability."),
    ],
    4: [
        ("h", "Retrieve -> score -> rerank"),
        ("b", "Recall funnel: fast structured score over all 100k -> keep a top pool."),
        ("b", "Semantic: bge-small-en-v1.5 cosine to a distilled JD query, blended 50/50 with lexical "
              "concept matching."),
        ("b", "Rerank: bge-reranker-v2-m3 cross-encoder takes half-authority over the top tier (drives NDCG@10)."),
        ("b", "Components (weighted): relevance .30, title/career .28, skill-depth .20, experience .12, "
              "education .10."),
        ("b", "Multipliers: penalties (services x0.45, CV/speech x0.6, title-chaser x0.85, location) x "
              "behavioral modifier (0.5-1.15)."),
        ("b", "Final: score = fit x penalties x behavioral; sort desc, tie-break by candidate_id (matches "
              "the validator). Models run offline; rank.py reads cached JSON."),
    ],
    5: [
        ("h", "How ranking decisions are explained"),
        ("b", "Every candidate carries a component breakdown + relevance parts (lexical / semantic / "
              "cross-encoder) and a 1-2 sentence reasoning string, shown in the demo UI."),
        ("h", "Preventing hallucinations / unsupported justifications"),
        ("b", "Reasoning is templated STRICTLY from real profile facts - no LLM in the output path - so a "
              "claim cannot reference anything not in the profile. Honest concerns stated; tone matches rank."),
        ("h", "Handling inconsistent / suspicious profiles"),
        ("b", "Honeypot/impossibility filter (e.g., expert skill with 0 months used; duration > career span). "
              "Calibrated to 65 impossible profiles with 0 false positives; 0 reach the top-100."),
    ],
    6: [
        ("h", "Complete workflow: JD input -> ranked output"),
        ("b", "OFFLINE (GPU ok, one-time): embed the candidate pool + cross-encoder rerank -> cache "
              "artifacts/*.json."),
        ("b", "SCORED (rank.py, CPU/offline, <=5 min): stream 100k -> honeypot filter -> component scoring "
              "x behavioral multiplier -> top-100 heap -> fact-grounded reasoning -> submission.csv."),
        ("b", "Validate: data/validate_submission.py confirms format before upload."),
        ("note", "Full workflow diagram: docs/05_approach_and_roadmap.md"),
    ],
    7: [
        ("h", "Components"),
        ("b", "src/ ranker: data_loader (streaming) - jd_profile (gated rubric + distilled query) - "
              "honeypot - features - scoring (semantic + lexical + rerank + behavioral) - reasoning - rank.py (CLI)."),
        ("b", "scripts/precompute.py - offline, GPU: embeddings + cross-encoder -> JSON artifacts."),
        ("b", "Demo: app/ (FastAPI) + frontend/ (Vite + React + Tailwind) -> single Docker image (HF Space)."),
        ("h", "Compliance boundary"),
        ("b", "GPU / transformers only in precompute; rank.py is stdlib, CPU-only, offline."),
        ("note", "Paste the architecture diagram here -> docs/05_approach_and_roadmap.md"),
    ],
    8: [
        ("h", "Results demonstrating ranking quality"),
        ("b", "Validator passes (100 rows, ranks 1-100, scores non-increasing, tie-break by id)."),
        ("b", "Honeypots in top-100: 0 - clears the >10% hard disqualifier."),
        ("b", "Quality (proxy, ground truth is hidden): top-100 -> 83 in-band, 97 show ranking work, only "
              "1 junior, 92 available. Top-10 are senior product-company retrieval/ranking/NLP engineers "
              "(Meta, Apple, Netflix, Zomato, Paytm, Razorpay...), 5.9-7.9 yrs."),
        ("h", "Meeting the runtime / compute constraints"),
        ("b", "rank.py: ~190s, CPU-only, offline, <16 GB (the only GPU step is offline precompute)."),
        ("note", "Method validated by a 3-way query ablation + full-100k negative calibration (docs/09)."),
    ],
    9: [
        ("h", "Technologies & why"),
        ("b", "Ranker: Python 3.13, stdlib-only - deliberate, guarantees CPU/offline reproducibility at Stage 3."),
        ("b", "Offline precompute: PyTorch + sentence-transformers; bge-small-en-v1.5 (embeddings) + "
              "bge-reranker-v2-m3 (cross-encoder) - open-source, no hosted API (Cohere excluded: network)."),
        ("b", "Demo: FastAPI; Vite + React + TypeScript + Tailwind; Recharts."),
        ("b", "Tooling: uv (reproducible envs, no pip); just (cross-platform tasks); Docker (HF Space)."),
        ("note", "Every choice keeps the scored path inside the compute budget while heavy models run offline."),
    ],
    10: [
        ("h", "Submission assets"),
        ("b", "GitHub (public): https://github.com/tsathya98/redrob-candidate-ranker"),
        ("s", "code, docs, single reproduce command: just rank"),
        ("b", "Ranked output: submission.xlsx (top-100, candidate_id / rank / score / reasoning)."),
        ("b", "This deck (PDF) - approach, methodology, results."),
        ("b", "Docs: README + docs/00-09 + docs/PROJECT_LOG.md (the iteration trail)."),
        ("s", "Run the demo locally: just serve (FastAPI + React) or just docker-run."),
    ],
    11: [
        ("h", "We'd rather surface 10 great matches than 1000 maybes."),
        ("note", "- the JD's words, and our design goal."),
        ("b", "Thank you.  Team: TODO  -  contact: TODO"),
    ],
}

TITLE_FIELDS = {  # slide 1: prefix -> filled value
    "Team Name": "TODO",
    "Team Leader Name": "TODO",
    "Problem Statement": ("Rank the top-100 best-fit candidates from a 100,000-profile pool for the "
                          "Senior AI Engineer (Founding Team) @ Redrob AI role - contextual + behavioral "
                          "fit over keyword overlap, CPU-only and offline (<=5 min)."),
}


def style(run, size, color, bold=False, italic=False):
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic


def fill_body(tf, items):
    tf.word_wrap = True
    tf.clear()
    first = True
    for kind, text in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        no_bullet(p)
        if kind == "h":
            p.space_before = Pt(6); p.space_after = Pt(2)
            r = p.add_run(); r.text = text; style(r, 13, HEAD, bold=True)
        elif kind == "note":
            p.space_after = Pt(2)
            r = p.add_run(); r.text = text; style(r, 10.5, MUTE, italic=True)
        elif kind == "s":
            p.level = 1; p.space_after = Pt(1)
            r = p.add_run(); r.text = "- " + text; style(r, 10.5, BODY)
        else:  # bullet
            p.space_after = Pt(2)
            r = p.add_run(); r.text = "•  " + text; style(r, 11, BODY)


def body_shape(slide):
    cand = [s for s in slide.shapes if s.has_text_frame and Emu(s.top).inches > 1.2
            and Emu(s.height).inches < 5.0]
    return max(cand, key=lambda s: Emu(s.width).inches * Emu(s.height).inches, default=None)


def main():
    prs = Presentation(str(TEMPLATE))
    slides = list(prs.slides)

    # slide 1 fields
    for sh in slides[0].shapes:
        if not sh.has_text_frame:
            continue
        for prefix, val in TITLE_FIELDS.items():
            if sh.text_frame.text.strip().startswith(prefix):
                tf = sh.text_frame
                tf.word_wrap = True
                tf.clear()
                r = tf.paragraphs[0].add_run()
                r.text = f"{prefix} : {val}"
                style(r, 12 if prefix != "Problem Statement" else 11, BODY,
                      bold=(prefix != "Problem Statement"))

    # content slides
    for n, items in CONTENT.items():
        slide = slides[n - 1]
        bs = body_shape(slide)
        if bs is None:  # e.g. slide 7 / 11 have no body box -> add one
            bs = slide.shapes.add_textbox(Inches(0.5), Inches(1.4), Inches(9.0), Inches(3.6))
        fill_body(bs.text_frame, items)

    prs.save(str(OUT))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
