#!/bin/bash
# Mac: double-click this file (first time: right-click > Open).   Linux: ./start.command
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
    python3 -m tidymate
else
    echo "Python 3 is not installed. Get it from https://www.python.org/downloads/"
fi
read -p "Press Enter to close..."
