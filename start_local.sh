#!/usr/bin/env bash
#
# One-time local setup for v3: creates the backend virtualenv, installs Python and
# frontend dependencies, ensures the MolScribe checkpoint is available, and writes
# backend/.env. Re-running is safe (idempotent).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_VENV="$BACKEND_DIR/.venv"
BACKEND_ENV_FILE="$BACKEND_DIR/.env"
MODEL_DIR="$BACKEND_DIR/models/molscribe"
MODEL_FILE="$MODEL_DIR/swin_base_char_aux_1m680k.pth"
# Reuse the checkpoint already downloaded under v2 if present, to avoid a second
# ~1GB download.
V2_MODEL_FILE="$ROOT_DIR/../v2/backend/models/molscribe/swin_base_char_aux_1m680k.pth"

# Pick a Python interpreter the pinned stack actually supports BEFORE touching PATH.
# The pins (torch 1.13.1, rdkit 2022.9.5, ...) only ship wheels for CPython 3.9/3.10,
# so a newer default python3 (e.g. Homebrew 3.13) would fail to resolve torch. We
# search 3.10 then 3.9 explicitly and fall back to python3 only if it is in range.
select_python() {
  local candidate version minor
  for candidate in python3.10 python3.9 python3; do
    command -v "$candidate" >/dev/null 2>&1 || continue
    version="$("$candidate" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null)" || continue
    minor="${version#3.}"
    if [ "${version%%.*}" = "3" ] && { [ "$minor" = "9" ] || [ "$minor" = "10" ]; }; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

if ! PYTHON_BIN="$(select_python)"; then
  echo "No compatible Python found. This project pins torch 1.13.1 / rdkit 2022.9.5,"
  echo "which require CPython 3.9 or 3.10. Please install one (e.g. via pyenv or conda)."
  echo "On Apple Silicon, torch 1.13.1 only has x86_64 wheels, so use an x86_64 Python"
  echo "(e.g. miniconda's python3.9) — an arm64 3.9 will also fail to find torch."
  exit 1
fi
PYTHON_BIN="$(command -v "$PYTHON_BIN")"
echo "==> Using Python: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

# Now safe to extend PATH for the node/npm checks below.
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
for tool in node npm; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "$tool is not installed or not on PATH. Please install Node.js first."
    exit 1
  fi
done

echo "==> Creating backend virtual environment"
# Drop any existing venv built with an incompatible interpreter (e.g. a failed
# earlier run that picked the wrong python), otherwise pip would fail again.
if [ -d "$BACKEND_VENV" ]; then
  existing="$("$BACKEND_VENV/bin/python" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "")"
  if [ "$existing" != "3.9" ] && [ "$existing" != "3.10" ]; then
    echo "    Removing incompatible existing venv (Python '${existing:-unknown}')"
    rm -rf "$BACKEND_VENV"
  fi
fi
if [ ! -d "$BACKEND_VENV" ]; then
  "$PYTHON_BIN" -m venv "$BACKEND_VENV"
fi
source "$BACKEND_VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r "$BACKEND_DIR/requirements.txt"

echo "==> Ensuring MolScribe checkpoint"
mkdir -p "$MODEL_DIR"
if [ -f "$MODEL_FILE" ]; then
  echo "    Already present: $MODEL_FILE"
  MOLSCRIBE_MODEL_PATH="$MODEL_FILE"
elif [ -f "$V2_MODEL_FILE" ]; then
  echo "    Reusing v2 checkpoint: $V2_MODEL_FILE"
  MOLSCRIBE_MODEL_PATH="$V2_MODEL_FILE"
else
  echo "    Downloading from Hugging Face..."
  python - <<EOF
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id="yujieq/MolScribe",
    filename="swin_base_char_aux_1m680k.pth",
    local_dir=r"$MODEL_DIR",
    local_dir_use_symlinks=False,
)
EOF
  MOLSCRIBE_MODEL_PATH="$MODEL_FILE"
fi

echo "==> Writing $BACKEND_ENV_FILE"
cat > "$BACKEND_ENV_FILE" <<EOF
MODEL_DEVICE=cpu
MOLSCRIBE_MODEL_PATH=$MOLSCRIBE_MODEL_PATH
EOF

echo "==> Installing frontend dependencies"
cd "$FRONTEND_DIR"
npm install

echo
echo "Setup complete. Start the app with:"
echo "  bash $ROOT_DIR/start_all.sh"
