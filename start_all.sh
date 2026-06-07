#!/usr/bin/env bash
#
# Start the v3 backend (FastAPI on :8000) and frontend (Vite on :5173) together.
# Run start_local.sh once first. Ctrl+C stops both.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_VENV="$BACKEND_DIR/.venv"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

if [ ! -d "$BACKEND_VENV" ] || [ ! -f "$BACKEND_DIR/.env" ] || [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Setup is incomplete. Run: bash $ROOT_DIR/start_local.sh"
  exit 1
fi

cleanup() {
  local exit_code=$?
  [ -n "${FRONTEND_PID:-}" ] && kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" >/dev/null 2>&1 || true
  wait >/dev/null 2>&1 || true
  exit "$exit_code"
}
trap cleanup EXIT INT TERM

# --- backend ---
set -a
source "$BACKEND_DIR/.env"
set +a
if [ ! -f "${MOLSCRIBE_MODEL_PATH:-}" ]; then
  echo "MolScribe model not found: ${MOLSCRIBE_MODEL_PATH:-<unset>}"
  echo "Run: bash $ROOT_DIR/start_local.sh"
  exit 1
fi
export PYTHONPATH="$BACKEND_DIR"
(
  cd "$BACKEND_DIR"
  echo "Backend  -> http://127.0.0.1:8000"
  exec "$BACKEND_VENV/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir app
) &
BACKEND_PID=$!

sleep 2

# --- frontend ---
(
  cd "$FRONTEND_DIR"
  echo "Frontend -> http://127.0.0.1:5173"
  exec npm run dev -- --host 127.0.0.1 --port 5173
) &
FRONTEND_PID=$!

echo
echo "Press Ctrl+C to stop both services."
wait "$BACKEND_PID" "$FRONTEND_PID"
