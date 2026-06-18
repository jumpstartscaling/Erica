#!/usr/bin/env bash
# Start Tranzformation Nation on http://localhost:8000 (one command).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv"
if [ ! -d "$VENV" ]; then
  echo "[run] creating virtualenv…"
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "[run] installing dependencies…"
pip install -q --disable-pip-version-check -r backend/requirements.txt

if [ ! -f backend/.env ]; then
  echo "[run] creating backend/.env from .env.example"
  cp backend/.env.example backend/.env
fi

# Load env vars from backend/.env
set -a
# shellcheck disable=SC1091
source backend/.env
set +a

echo "[run] starting uvicorn → http://localhost:8000"
cd backend
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
