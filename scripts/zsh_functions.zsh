# Minimal zsh helper: `a` appends a timestamped line to constraints.md
# Usage: a your message here

a() {
  local msg
  msg="$*"
  if [[ -z "$msg" ]]; then
    echo "usage: a <message>" >&2
    return 2
  fi
  # Call the tiny Python helper (keeps shell minimal and consistent with app logic)
  local repo_root
  repo_root="${${(%):-%x}:A:h:h}"  # this file's dir -> repo root
  python3 "$repo_root/scripts/constraints_add_entry.py" -- "$msg"
}

