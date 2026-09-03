#!/bin/bash
# Run this on your own machine, not in a cloud session — it starts a
# server bound to localhost and a real Chrome/Chromium browser.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs

if [ ! -f .env ]; then
  echo "Missing .env — copy .env.example to .env and fill in your credentials first." >&2
  exit 1
fi

node src/dashboard-server.js > logs/dashboard.log 2>&1 &
echo $! > .dashboard.pid
node src/automation/job-processor.js > logs/processor.log 2>&1 &
echo $! > .processor.pid

echo "Dashboard: http://localhost:${DASHBOARD_PORT:-3000}"
echo "Logs: logs/dashboard.log, logs/processor.log"
echo "Stop with: bash stop-automation.sh"
