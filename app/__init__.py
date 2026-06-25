"""FastAPI demo backend for the Redrob candidate ranker.

Wraps the offline `src/` ranking pipeline behind a small API so the React UI (the mandatory sandbox)
can show the ranking, score breakdowns, "reading between the lines" evidence, trap/honeypot detection,
and an optional (clearly-separated) LLM narration. The scored ranking itself remains 100% offline.
"""
