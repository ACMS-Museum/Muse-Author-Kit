#!/usr/bin/env bash

set -euo pipefail

PYTHON_EXE="${PYTHON_EXE:-python3}"

if ! command -v "$PYTHON_EXE" >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_EXE="python"
  else
    echo "Could not find python3 or python on PATH."
    exit 1
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$KIT_ROOT/.venv"
WHEEL_DIR="$KIT_ROOT/packages"
GAME_ROOT="$KIT_ROOT/muse-game"

echo "Creating virtual environment..."
"$PYTHON_EXE" -m venv "$VENV_PATH"

VENV_PYTHON="$VENV_PATH/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
  echo "Could not find virtual environment Python at $VENV_PYTHON"
  exit 1
fi

echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

echo "Installing Evennia..."
"$VENV_PYTHON" -m pip install evennia

WHEEL_PATH="$(find "$WHEEL_DIR" -maxdepth 1 -type f -name 'muselang-*.whl' | head -n 1)"
if [ -z "$WHEEL_PATH" ]; then
  echo "Could not find a MuseLang wheel in $WHEEL_DIR"
  exit 1
fi

echo "Installing MuseLang from wheel..."
"$VENV_PYTHON" -m pip install "$WHEEL_PATH"

echo "Installing MuseLang runtime into muse-game..."
"$VENV_PYTHON" -m muselang.cli runtime-install --game-root "$GAME_ROOT"
"$VENV_PYTHON" -m muselang.cli doctor --game-root "$GAME_ROOT"

echo
echo "Muse Author Kit install complete."
echo "MuseLang is installed into ./.venv and the muse-game scaffold is ready."
echo "Next steps:"
echo "  1. source ./.venv/bin/activate"
echo "  2. cd ./muse-game"
echo "  3. evennia migrate"
echo "  4. evennia createsuperuser"
echo "  5. evennia start"
