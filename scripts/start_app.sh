#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
APP_URL="http://127.0.0.1:5173"
API_URL="http://127.0.0.1:8000/health"
BACKEND_PID=""
FRONTEND_PID=""

open_app() {
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$APP_URL" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$APP_URL" >/dev/null 2>&1 || true
  fi
}

wait_for_url() {
  local url="$1"
  for _ in {1..40}; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

cd "$BACKEND_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
if curl -fsS "$API_URL" >/dev/null 2>&1; then
  echo "Backend deja lance sur http://127.0.0.1:8000"
else
  uvicorn app.main:app --host 127.0.0.1 --port 8000 &
  BACKEND_PID=$!
  wait_for_url "$API_URL" || echo "Backend en cours de demarrage..."
fi

cleanup() {
  if [ -n "$BACKEND_PID" ]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [ -n "$FRONTEND_PID" ]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

cd "$FRONTEND_DIR"
npm install
if curl -fsS "$APP_URL" >/dev/null 2>&1; then
  echo "Frontend deja lance sur $APP_URL"
else
  npm run dev -- --host 127.0.0.1 &
  FRONTEND_PID=$!
  wait_for_url "$APP_URL" || echo "Frontend en cours de demarrage..."
fi

echo "Nutripuncture Desk est lance: $APP_URL"
open_app
if [ -n "$FRONTEND_PID" ]; then
  wait "$FRONTEND_PID"
else
  echo "Une instance existante est reutilisee. Fermez cette fenetre si tout est ouvert."
  while true; do sleep 3600; done
fi
