# Multi-stage build: compile the React UI, then serve it + the ranking API from FastAPI.
# Works as the Hugging Face Docker Space (sandbox) and as a `docker run` fallback.
# The ranking step inside is CPU-only and offline; the optional LLM panel activates only if
# ANTHROPIC_API_KEY is provided as a Space secret.

# --- stage 1: build frontend ---
FROM node:22-slim AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- stage 2: python runtime ---
FROM python:3.11-slim AS app
# uv: fast, reproducible installs (https://github.com/astral-sh/uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1 \
    UV_NO_CACHE=1 \
    UV_SYSTEM_PYTHON=1 \
    HF_HOME=/tmp/hf \
    PORT=7860
WORKDIR /srv

COPY app/requirements.txt ./app/requirements.txt
RUN uv pip install --system -r app/requirements.txt

# ranking package + service + demo sample
COPY src/ ./src/
COPY app/ ./app/
# built frontend assets (served by FastAPI at /)
COPY --from=web /web/dist ./frontend/dist

EXPOSE 7860
# shell form so $PORT (HF sets it) is expanded
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}
