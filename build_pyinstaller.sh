#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

python -m PyInstaller --noconfirm --clean --onefile --name deadinside_desktop main.py

mkdir -p dist/linux
if [ -f "dist/deadinside_desktop" ]; then
  cp "dist/deadinside_desktop" "dist/linux/"
fi
if [ -f "dist/deadinside_desktop.exe" ]; then
  cp "dist/deadinside_desktop.exe" "dist/linux/"
fi

if [ -d "dist/linux" ]; then
  tar -czf dist/deadinside_linux.tar.gz -C dist linux
fi
