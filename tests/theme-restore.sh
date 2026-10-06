#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir "$tmp/bin"
cat > "$tmp/bin/crush" <<'MOCK'
#!/usr/bin/env bash
[[ "$(jq -r .theme "$CRUSH_CONFIG")" == ultralovegod ]] || exit 99
exit "${MOCK_EXIT:-0}"
MOCK
chmod +x "$tmp/bin/crush"
for expected in 0 7; do
  printf '{"theme":"original","keep":true}\n' > "$tmp/config.json"
  cp "$tmp/config.json" "$tmp/original.json"
  actual=0
  PATH="$tmp/bin:$PATH" CRUSH_CONFIG="$tmp/config.json" MOCK_EXIT="$expected" \
    bash "$root/bin/crush-love-dev" --apply >/dev/null || actual=$?
  [[ "$actual" == "$expected" ]] || { echo 'child exit status changed'; exit 1; }
  cmp "$tmp/original.json" "$tmp/config.json"
done
echo 'theme restored after successful and failed child exits'
