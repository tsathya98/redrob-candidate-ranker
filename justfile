# Redrob Candidate Ranker — task runner (https://just.systems)
# Cross-platform: works on Windows (PowerShell) and Linux/macOS (sh).
# Toolchain: uv (Python, no pip), npm (frontend). Install just: `uv tool install rust-just`
# or scoop/choco/brew/cargo. Then run `just` to list recipes.

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# show available recipes
default:
    @just --list

# --- setup -------------------------------------------------------------------

# install everything: backend venv (uv) + frontend deps (npm)
install: install-backend install-frontend

# create the uv venv and install backend/demo deps (no pip)
install-backend:
    uv venv
    uv pip install -r app/requirements.txt

# install frontend dependencies
install-frontend:
    npm --prefix frontend install

# --- ranking pipeline (the scored deliverable) -------------------------------

# run the offline ranker -> submission.csv (CPU-only, no network)
rank:
    uv run python src/rank.py --candidates data/candidates.jsonl --out submission.csv

# validate the submission CSV against the challenge format rules
validate:
    uv run python data/validate_submission.py submission.csv

# rank then validate
check: rank validate

# --- Slice 2: offline precompute (semantic embeddings + cross-encoder reranker) ----

# install precompute deps (CPU torch + sentence-transformers) — one-time, offline-capable after
precompute-install:
    uv pip install torch --index-url https://download.pytorch.org/whl/cpu
    uv pip install -r requirements-precompute.txt

# precompute artifacts for the full pool -> artifacts/ (offline, may exceed 5 min; one-time)
precompute:
    uv run python scripts/precompute.py --candidates data/candidates.jsonl --out artifacts

# precompute artifacts for the 80-candidate demo sample (committed for the sandbox)
precompute-demo:
    uv run python scripts/precompute.py --candidates app/demo_data/demo_candidates.jsonl --out app/demo_data/artifacts --shortlist 80

# --- demo UI (the sandbox) ---------------------------------------------------

# run the FastAPI backend (API at :8000; also serves frontend/dist if built)
api:
    uv run uvicorn app.main:app --port 8000

# run the frontend dev server (hot reload, proxies /api -> :8000)
web:
    npm --prefix frontend run dev

# build the frontend for production -> frontend/dist
build-web:
    npm --prefix frontend run build

# production-style single origin: build UI, then serve UI + API on :8000
serve: build-web
    uv run uvicorn app.main:app --port 8000

# --- container / deploy ------------------------------------------------------

# build the single-image sandbox (UI + API)
docker-build:
    docker build -t redrob-ranker .

# run the container (sandbox at http://localhost:7860)
docker-run:
    docker run --rm -p 7860:7860 redrob-ranker
