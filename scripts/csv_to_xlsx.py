#!/usr/bin/env python3
"""Convert the ranked submission CSV -> XLSX (the portal upload format).

The repo/validator use CSV (submission_spec); the Hack2Skill portal asks for the ranked output as XLSX.
Same 100 rows + header, with rank as int and score as float, and a styled header row.

  uv run python scripts/csv_to_xlsx.py submission.csv submission/submission.xlsx
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import xlsxwriter


def main(argv: list[str]) -> int:
    src = Path(argv[0]) if argv else Path("submission.csv")
    out = Path(argv[1]) if len(argv) > 1 else Path("submission/submission.xlsx")
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(src, encoding="utf-8")))

    wb = xlsxwriter.Workbook(str(out))
    ws = wb.add_worksheet("ranking")
    head = wb.add_format({"bold": True, "bg_color": "#1F2937", "font_color": "white", "border": 1})
    cell = wb.add_format({"border": 1, "valign": "top"})
    wrap = wb.add_format({"border": 1, "valign": "top", "text_wrap": True})

    cols = ["candidate_id", "rank", "score", "reasoning"]
    for c, name in enumerate(cols):
        ws.write(0, c, name, head)
    for r, row in enumerate(rows, start=1):
        ws.write_string(r, 0, row["candidate_id"], cell)
        ws.write_number(r, 1, int(row["rank"]), cell)
        ws.write_number(r, 2, float(row["score"]), cell)
        ws.write_string(r, 3, row["reasoning"], wrap)
    ws.set_column(0, 0, 16)
    ws.set_column(1, 1, 6)
    ws.set_column(2, 2, 10)
    ws.set_column(3, 3, 90)
    ws.freeze_panes(1, 0)
    wb.close()
    print(f"wrote {out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
