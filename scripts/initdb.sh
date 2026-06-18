#!/usr/bin/env bash
# Initialize + seed the database (SQLite by default; Postgres if DATABASE_URL set).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv"
if [ ! -d "$VENV" ]; then
  echo "[initdb] creating virtualenv…"
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "[initdb] installing dependencies…"
pip install -q --disable-pip-version-check -r backend/requirements.txt

if [ ! -f backend/.env ]; then
  echo "[initdb] creating backend/.env from .env.example"
  cp backend/.env.example backend/.env
fi

set -a
# shellcheck disable=SC1091
source backend/.env
set +a

cd backend
python -c "import db, json; print('[initdb]', json.dumps(db.init_db()))"
echo "[initdb] done. Demo admin: admin@example.com / password"
