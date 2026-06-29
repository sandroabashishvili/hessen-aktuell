#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

: "${HESSEN_AKTUELL_BASE_URL:=https://sandroabashishvili.github.io/hessen-aktuell}"
export HESSEN_AKTUELL_BASE_URL

python3 -m shared.py.news_pipeline
python3 -m shared.py.diagnostics

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git status --short
  if [[ "${AUTO_COMMIT:-0}" == "1" ]]; then
    git add .
    if git diff --cached --quiet; then
      echo "No generated changes to commit."
    else
      git commit -m "Update Hessen Aktuell generated site"
      git push
    fi
  fi
else
  echo "Not a git repository yet; generation and diagnostics completed only."
fi
