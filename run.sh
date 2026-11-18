#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt
python assignments/capstone/app.py --demo
printf '\nDemo finished. Full checker: python -m autograde.run --capstone --root . -v\n'
