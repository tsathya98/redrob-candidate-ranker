#!/usr/bin/env python3
"""Deploy the demo as a Hugging Face Docker Space (the live sandbox).

One-time auth first (paste a WRITE token from https://huggingface.co/settings/tokens):
    hf auth login            # or: huggingface-cli login

Then:
    uv run python scripts/deploy_hf_space.py [space_name]

The Dockerfile at repo root builds the React UI + serves the FastAPI ranker on $PORT (7860). The Space
runs CPU-only and ships precomputed demo artifacts, so it needs no GPU and no secrets.
"""
from __future__ import annotations

import sys

from huggingface_hub import HfApi

SPACE_README = """---
title: Redrob Candidate Ranker
emoji: "\U0001F3AF"
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
short_description: Intelligent candidate discovery & ranking
---

# Redrob Intelligent Candidate Discovery -- live demo

Hybrid, explainable, CPU-only candidate ranker: honeypot filter -> JD gated rubric -> semantic + lexical
relevance -> cross-encoder rerank -> bounded behavioral multiplier -> fact-grounded reasoning. This Space
runs the demo on a small bundled sample.

Code & docs: https://github.com/tsathya98/redrob-candidate-ranker
"""

# Only what the Docker build needs (Dockerfile, src/, app/, frontend/ source). Everything heavy/irrelevant
# is excluded so the Space repo stays small and builds fast.
IGNORE = [
    ".git/**", ".git*", "data/**", "old/**", ".venv/**", "venv/**", "env/**",
    "**/__pycache__/**", "**/node_modules/**", "frontend/dist/**",
    "submission/**", "artifacts/**", "/artifacts/**", "docs/images/**",
    "*.csv", "*.xlsx", "*.pptx", "*.pdf", "*.npy", "README.md",
]


def main(argv: list[str]) -> int:
    name = argv[0] if argv else "redrob-candidate-ranker"
    api = HfApi()
    try:
        who = api.whoami()["name"]
    except Exception:
        print("Not logged in. Run:  hf auth login   (paste a WRITE token), then re-run this script.",
              file=sys.stderr)
        return 1
    repo_id = f"{who}/{name}"
    print(f"creating Docker Space: {repo_id}")
    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", exist_ok=True)

    print("uploading code (Dockerfile, src/, app/, frontend/ source) ...")
    api.upload_folder(repo_id=repo_id, repo_type="space", folder_path=".",
                      ignore_patterns=IGNORE, commit_message="deploy demo sandbox")
    # Space README carries the required docker frontmatter (uploaded last so it is authoritative)
    api.upload_file(path_or_fileobj=SPACE_README.encode(), path_in_repo="README.md",
                    repo_id=repo_id, repo_type="space", commit_message="space metadata")

    url = f"https://huggingface.co/spaces/{repo_id}"
    print(f"\nDONE -> {url}")
    print("First build takes a few minutes (npm build + uv install). Watch the Space 'Logs' tab.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
