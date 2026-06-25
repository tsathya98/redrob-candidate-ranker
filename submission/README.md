# Submission folder — upload checklist

The Hack2Skill portal (Data & AI Challenge) asks for exactly three things. Everything is in this folder.

| # | Portal field | File to upload | Status |
|---|---|---|---|
| 1 | GitHub repository (public) | `https://github.com/tsathya98/redrob-candidate-ranker` | ✅ public |
| 2 | PPT/deck **as PDF** (≤5 MB) | **`Redrob_Idea_Submission.pdf`** (~0.5 MB) | ✅ ready |
| 3 | Ranked output **as XLSX** (≤5 MB) | **`submission.xlsx`** (top-100) | ✅ ready |

### Before you upload — fill 2 fields on the deck
The deck still has `TODO` for **Team Name** and **Team Leader Name** (slides 1 & 11). Either:
- tell the agent the two values and it will regenerate the PDF, **or**
- open `Redrob_Idea_Submission.pptx` (or the Google-Slides template copy) → edit slides 1 & 11 →
  export to PDF. (Deadline: **2 July 2026, 11:59 PM IST**.)

### Files here
- `Redrob_Idea_Submission.pdf` — the approach deck (upload this). *Built from the organizer template.*
- `Redrob_Idea_Submission.pptx` — editable deck (git-ignored; for last-minute edits).
- `submission.xlsx` — the ranked top-100 (upload this). *git-ignored — the public repo must not leak answers.*
- `Idea Submission Template _ Redrob.pptx` — the original organizer template (git-ignored).
- `DECK_CONTENT.md` — the slide-by-slide source content.

### Regenerate any of these
```bash
just check                                   # rank -> submission.csv (validated)
uv run python scripts/csv_to_xlsx.py         # submission.csv -> submission/submission.xlsx
uv run python scripts/build_deck.py          # fill template -> submission/Redrob_Idea_Submission.pptx
# PPTX -> PDF: open in PowerPoint/Google Slides -> export PDF (or LibreOffice --convert-to pdf)
```
