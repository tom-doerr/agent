#!/usr/bin/env bash
set -euo pipefail

# Minimal forbid-list for staged files (or provided paths).
# Blocks committing these repo-root files: constraints.md, memory.md,
# short_term_memory.md, notes.md, info.md

deny=(
  "constraints.md"
  "memory.md"
  "short_term_memory.md"
  "notes.md"
  "info.md"
)

targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  # Only from index; added/copied/modified/renamed
  mapfile -t targets < <(git diff --cached --name-only --diff-filter=ACMR)
fi

if [ ${#targets[@]} -eq 0 ]; then
  exit 0
fi

violations=()
for f in "${targets[@]}"; do
  # Match by basename to catch staged files regardless of relative path
  bn=$(basename -- "$f")
  case "$bn" in
    constraints.md|memory.md|short_term_memory.md|notes.md|info.md)
      violations+=("$f")
      ;;
  esac
done

if [ ${#violations[@]} -gt 0 ]; then
  echo "Blocked committing sensitive Markdown file(s):" >&2
  for v in "${violations[@]}"; do echo "  - $v" >&2; done
  echo "These files are local state and must remain untracked (.gitignored)." >&2
  exit 1
fi

exit 0
