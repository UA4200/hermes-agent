#!/bin/bash
cd "$(dirname "$0")"
for pidfile in .dashboard.pid .processor.pid; do
  if [ -f "$pidfile" ]; then
    kill "$(cat "$pidfile")" 2>/dev/null || true
    rm -f "$pidfile"
  fi
done
echo "Automation stopped."
