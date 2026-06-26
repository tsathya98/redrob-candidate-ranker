#!/usr/bin/env python3
"""Assemble the ~2000 window-top-100 finalists into one file for the final Opus rerank."""
from __future__ import annotations
import glob, json
from pathlib import Path

V = Path("/home/tsath/.claude/jobs/80528b4c/tmp/llmval")

def main():
    # id -> best window-LLM score (a candidate appears in exactly one window, so this is its window score)
    final = {}
    for f in sorted(glob.glob(str(V / "out_*.json"))):
        for o in json.load(open(f)):
            cid = o["candidate_id"]
            final[cid] = max(final.get(cid, -1), int(o.get("score", 0)))
    # id -> compact profile line (from the window files)
    line = {}
    for f in sorted(glob.glob(str(V / "win_*.txt"))):
        for ln in open(f, encoding="utf-8"):
            if ln.strip():
                line[ln.split(" | ", 1)[0].strip()] = ln.rstrip("\n")
    rows = []
    for cid, sc in final.items():
        if cid in line:
            rows.append((sc, line[cid]))
    rows.sort(key=lambda t: -t[0])
    out = V / "finalists.txt"
    out.write_text("\n".join(f"[win_score={sc}] {ln}" for sc, ln in rows), encoding="utf-8")
    json.dump(sorted(final), open(V / "finalist_ids.json", "w"))
    print(f"finalists: {len(rows)} unique candidates -> {out}")
    print("size:", out.stat().st_size, "bytes")

if __name__ == "__main__":
    main()
