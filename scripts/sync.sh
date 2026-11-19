#!/usr/bin/env bash
# Pull, commit everything that changed under the shared folders, push.
# Usage: bash scripts/sync.sh "one-line message"
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
msg="${1:-sync}"
git pull --rebase --autostash
for p in BOARD.md STATUS.md TASKS.md runs inverse docs/RESULTS.md; do
  [ -e "$p" ] && git add "$p"
done
# refuse large files
big=$(git diff --cached --name-only | while read -r f; do [ -f "$f" ] && [ "$(wc -c <"$f")" -gt 5242880 ] && echo "$f"; done || true)
if [ -n "$big" ]; then echo "Files over 5 MB staged, not committing:"; echo "$big"; exit 1; fi
if git diff --cached --quiet; then echo "nothing to commit"; else git commit -m "$msg"; fi
git push
