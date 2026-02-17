#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-/opt/homebrew/bin/python3.12}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "ERROR: PYTHON_BIN not found/executable: $PYTHON_BIN" >&2
  echo "Install Python 3.12 (brew install python@3.12) or set PYTHON_BIN." >&2
  exit 1
fi

# Ensure venv exists and matches the desired interpreter.
if [[ -d ".venv" ]]; then
  VENV_PY=".venv/bin/python"
  if [[ -x "$VENV_PY" ]]; then
    VENV_VER="$($VENV_PY -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    if [[ "$VENV_VER" != "3.12" ]]; then
      echo "Rebuilding venv: found Python $VENV_VER, expected 3.12" >&2
      rm -rf .venv
    fi
  else
    rm -rf .venv
  fi
fi

if [[ ! -d ".venv" ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

exec python main.py
