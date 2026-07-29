#!/usr/bin/env bash

# Regression test for system-info.sh's network-output safety contract.

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
test_dir=$(mktemp -d)

cleanup() {
  rm -rf -- "$test_dir"
}
trap cleanup EXIT

mock_ip="$test_dir/ip"
# These single-quoted arguments are literal source lines for the generated mock;
# their parameter expansions must occur later, when that mock runs.
# shellcheck disable=SC2016
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'separator=:' \
  'loopback_mac="00${separator}00${separator}00${separator}00${separator}00${separator}00"' \
  'ethernet_mac="aa${separator}bb${separator}cc${separator}dd${separator}ee${separator}ff"' \
  'printf "lo UNKNOWN %s\neth0 UP %s\n" "$loopback_mac" "$ethernet_mac"' \
  >"$mock_ip"
chmod +x "$mock_ip"

output=$(PATH="$test_dir:$PATH" bash "$repo_root/scripts/system-info.sh")

mac_pattern='(^|[^[:xdigit:]])([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}([^[:xdigit:]]|$)'
if grep -Eq "$mac_pattern" <<<"$output"; then
  echo "system-info.sh exposed a MAC address."
  exit 1
fi

grep -Fxq "lo UNKNOWN" <<<"$output"
grep -Fxq "eth0 UP" <<<"$output"

echo "system-info.sh network output passed the privacy regression test."
