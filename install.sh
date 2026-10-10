#!/bin/sh
# TidyMate - one-line installer for Mac / Linux.
#
#   curl -fsSL https://raw.githubusercontent.com/Anand2k29/TidyMate/main/install.sh | sh
#
# It creates a private Python environment (so nothing else on your computer is touched),
# installs the tool in it, and puts two commands - tidymate and start_here - in ~/.local/bin.
# Re-run it any time to update. Remove it with:  tidymate setup --uninstall && rm -rf ~/.tidymate/venv
set -eu

REPO="${TIDYMATE_REPO:-Anand2k29/TidyMate}"
SPEC="${TIDYMATE_SPEC:-https://github.com/$REPO/archive/refs/heads/main.zip}"   # or a folder path / PyPI name
ROOT="${TIDYMATE_HOME:-$HOME/.tidymate}"
VENV="$ROOT/venv"

PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && \
     "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
    PY="$candidate"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Python 3.8 or newer was not found. Install it from https://www.python.org/downloads/ and run this again."
  exit 1
fi

echo "==> Using $($PY --version)"
mkdir -p "$ROOT"
if [ ! -x "$VENV/bin/python" ]; then
  "$PY" -m venv "$VENV" || {
    echo "Could not create a virtual environment."
    echo "On Debian/Ubuntu run:  sudo apt install python3-venv   and try again."
    exit 1
  }
fi
echo "==> Installing TidyMate ..."
"$VENV/bin/python" -m pip install --quiet --upgrade "$SPEC"
echo "==> Creating the tidymate command ..."
"$VENV/bin/python" -m tidymate setup
