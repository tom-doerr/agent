#!/usr/bin/env bash
set -euo pipefail

# Minimal, high-confidence secret scan for staged files (or given paths).
# Patterns: private keys, GitHub tokens, GitHub PATs, AWS AKIA/ASIA, Slack webhooks, Bearer tokens.

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required. Install rg and retry." >&2
  exit 2
fi

shopt -s nullglob

patterns=(
  '-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'
  'ghp_[A-Za-z0-9]{36,}'
  'github_pat_[A-Za-z0-9_]{80,}'
  'AKIA[0-9A-Z]{16}'
  'ASIA[0-9A-Z]{16}'
  'hooks\.slack\.com/services/'
  'Authorization: Bearer [A-Za-z0-9_\-\.]+'
)

# Collect target files
targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  # Default: scan staged text files (added/copied/modified)
  mapfile -t targets < <(git diff --cached --name-only --diff-filter=ACM | rg -n -v '^$' | cut -d: -f1)
fi

if [ ${#targets[@]} -eq 0 ]; then
  exit 0
fi

# Filter existing readable files only
filtered=()
for f in "${targets[@]}"; do
  [ -f "$f" ] && [ -r "$f" ] && filtered+=("$f") || true
done

if [ ${#filtered[@]} -eq 0 ]; then
  exit 0
fi

args=( -n -I -P )
for p in "${patterns[@]}"; do args+=( -e "$p" ); done

set +e
rg "${args[@]}" -- "${filtered[@]}"
rc=$?
set -e

case "$rc" in
  0)
    echo
    echo "Secret-like strings detected above. Remove or mask before committing." >&2
    exit 1
    ;;
  1)
    # no matches
    exit 0
    ;;
  *)
    echo "Scan failed (rg exit $rc)." >&2
    exit $rc
    ;;
esac

