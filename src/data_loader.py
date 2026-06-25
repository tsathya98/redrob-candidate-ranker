"""Load and normalize the candidate pool.

Responsibilities (Phase 1):
- Stream-parse candidates.jsonl (100k lines, ~465 MB) without loading it all into memory at once
  where avoidable (generator-based), or materialize a compact in-memory representation that fits 16 GB.
- Normalize/validate fields against candidate_schema.json expectations.
- Build a single "candidate text blob" per candidate (summary + career descriptions + skills + headline)
  for the semantic-relevance component.

Nothing here makes network calls. See docs/02_dataset_and_signals.md for the schema.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterator


def iter_candidates(path: str | Path) -> Iterator[dict]:
    """Yield candidate dicts one at a time from a .jsonl or .jsonl.gz file.

    Streaming keeps memory flat regardless of pool size.
    """
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:  # type: ignore[operator]
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def candidate_text_blob(candidate: dict) -> str:
    """Concatenate the free-text fields used for semantic matching.

    TODO(Phase 4): tune which fields/weights go into the blob; consider per-section embeddings.
    """
    raise NotImplementedError("Phase 4: build the semantic text blob.")


def load_pool(path: str | Path) -> list[dict]:
    """Materialize the full pool (use only when 16 GB budget allows).

    TODO(Phase 1): decide between full materialization vs streaming for the ranking step.
    """
    raise NotImplementedError("Phase 1: implement pool loading strategy.")
