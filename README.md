# Python-Based-Command-Terminal
# CodeMate Terminal (Problem 1)

## Overview
A sandboxed Python terminal implementing file operations and system monitoring.

## Run (CLI)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/cli.py

## Run (Web)
pip install -r requirements.txt
python src/web_app.py
Open http://127.0.0.1:5000

## Features
- ls, cd, pwd, mkdir, rm, touch, cat, mv, cp, stat
- sysinfo (CPU/Memory), ps (process list)
- sandboxed to project folder

## Notes
Do not upload venv/ or node_modules/ to CodeMate.

## License
MIT
