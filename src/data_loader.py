"""Load and normalize the candidate pool.

- Stream-parse candidates.jsonl (100k lines) with a generator so memory stays flat.
- Build a "candidate text blob" per candidate (headline + summary + career descriptions + skills +
  education) for lexical (Slice 1) and semantic (Slice 2) matching.
- Small, dependency-free date helpers shared across modules.

No network calls. See docs/02_dataset_and_signals.md for the schema.
"""

from __future__ import annotations

import gzip
import json
from datetime import date
from pathlib import Path
from typing import Iterator, Optional


def iter_candidates(path: str | Path) -> Iterator[dict]:
    """Yield candidate dicts one at a time from a .jsonl or .jsonl.gz file."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:  # type: ignore[operator]
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def candidate_text_blob(candidate: dict) -> str:
    """Concatenate the free-text fields used for lexical/semantic matching (lowercased).

    Career-history *descriptions* are the highest-value signal (what the candidate actually built),
    so they are included in full — this is what lets us catch plain-language fits (docs/03 Trap 2).
    """
    parts: list[str] = []
    p = candidate.get("profile", {})
    parts.append(p.get("headline", ""))
    parts.append(p.get("summary", ""))
    parts.append(p.get("current_title", ""))
    parts.append(p.get("current_industry", ""))

    for job in candidate.get("career_history", []):
        parts.append(job.get("title", ""))
        parts.append(job.get("description", ""))

    for sk in candidate.get("skills", []):
        parts.append(sk.get("name", ""))

    for ed in candidate.get("education", []):
        parts.append(ed.get("degree", ""))
        parts.append(ed.get("field_of_study", ""))

    for cert in candidate.get("certifications", []):
        parts.append(cert.get("name", ""))

    return " ".join(s for s in parts if s).lower()


# --- shared date / number helpers -------------------------------------------------

def parse_date(s: Optional[str]) -> Optional[date]:
    """Parse an ISO 'YYYY-MM-DD' date; return None for null/blank/unparseable values."""
    if not s:
        return None
    try:
        y, m, d = (int(x) for x in s[:10].split("-"))
        return date(y, m, d)
    except (ValueError, TypeError):
        return None


def months_between(start: Optional[date], end: Optional[date]) -> Optional[int]:
    """Whole months between two dates (end defaults handled by caller). None if either is missing."""
    if start is None or end is None:
        return None
    return (end.year - start.year) * 12 + (end.month - start.month)
