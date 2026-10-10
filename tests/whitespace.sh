#!/usr/bin/env bash
# syntax + whitespace gate. a stray tab, a trailing space after a line
# continuation, or a CR sneaked in by a paste makes bash choke at the edit
# site with a misleading "syntax error near unexpected token `(" — this test
# catches that class before it reaches an interactive session.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail=0
files=("$root/bin/crush-love-dev")
while IFS= read -r f; do files+=("$f"); done < <(
  find "$root/scripts" "$root/tests" -type f -name '*.sh' 2>/dev/null | sort
)

for f in "${files[@]}"; do
  rel="${f#"$root"/}"
  bash -n "$f" 2>"$tmp/err" || { echo "syntax error: $rel"; cat "$tmp/err"; fail=1; }
  if LC_ALL=C grep -nq $'\t' "$f"; then
    echo "tab character: $rel"; LC_ALL=C grep -n $'\t' "$f"; fail=1
  fi
  if grep -nqE '[[:space:]]+$' "$f"; then
    echo "trailing whitespace: $rel"; grep -nE '[[:space:]]+$' "$f"; fail=1
  fi
  if grep -nq $'\r' "$f"; then
    echo "carriage return (CRLF): $rel"; fail=1
  fi
done

python3 -c 'import py_compile, sys
py_compile.compile(sys.argv[1], cfile=sys.argv[2], doraise=True)' \
  "$root/bin/crush-love-doctor" "$tmp/doctor.pyc" 2>"$tmp/pyerr" \
  || { echo "syntax error: bin/crush-love-doctor"; cat "$tmp/pyerr"; fail=1; }

[[ $fail -eq 0 ]] || exit 1
echo 'scripts: syntax clean, no tabs, no trailing whitespace, no CRLF'
