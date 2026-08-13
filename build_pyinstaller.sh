#!/usr/bin/env bash
# Build a single-file executable for desktop (Windows/Linux) using PyInstaller
pyinstaller --onefile --name deadinside_core -p . core/api.py
