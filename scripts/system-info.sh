#!/usr/bin/env bash

# Script: system-info.sh
# Purpose: Print public-safe system information for the Raspberry Pi home-server lab.
# Safety: This script does not print passwords, private keys, tokens, or secrets.

set -u

section() {
  echo
  echo "========================================"
  echo "$1"
  echo "========================================"
}

section "System Identity"
echo "Hostname: $(hostname)"
echo "Current user: $(whoami)"
echo "Date: $(date)"

section "Operating System"
if command -v lsb_release >/dev/null 2>&1; then
  lsb_release -a
elif [ -f /etc/os-release ]; then
  cat /etc/os-release
else
  echo "OS release information not found."
fi

section "Kernel"
uname -a

section "Uptime"
uptime

section "Memory"
free -h

section "Disk Usage"
df -h

section "CPU Info"
if [ -f /proc/cpuinfo ]; then
  grep -E "Model|Hardware|Revision|Serial|processor|model name" /proc/cpuinfo | head -n 20
else
  echo "CPU info not found."
fi

section "Temperature"
if command -v vcgencmd >/dev/null 2>&1; then
  vcgencmd measure_temp
elif [ -f /sys/class/thermal/thermal_zone0/temp ]; then
  temp_raw=$(cat /sys/class/thermal/thermal_zone0/temp)
  temp_c=$(awk "BEGIN {printf \"%.1f\", $temp_raw / 1000}")
  echo "CPU temperature: ${temp_c}°C"
else
  echo "Temperature information not available."
fi

section "Network Interfaces"
ip -brief addr 2>/dev/null || echo "ip command not available."

section "Docker Status"
if command -v docker >/dev/null 2>&1; then
  docker --version
  systemctl is-active docker 2>/dev/null || echo "Docker service status not available."
else
  echo "Docker is not installed or not available in PATH."
fi

section "End"
echo "System information check complete."
