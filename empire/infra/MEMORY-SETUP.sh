#!/bin/bash
# MEMORY SYSTEM SETUP — Safe to rerun (idempotent, snapshot-first).
# Creates the persistent brain structure for the empire.
# Existing files are backed up before any overwrite.
# Pass --dry-run to preview actions without writing anything.

set -euo pipefail

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

# ---------------------------------------------------------------------------
# Resolve HERMES_AGENT_HOME — never hard-code ~/hermes-agent
# ---------------------------------------------------------------------------
if [[ -n "${HERMES_AGENT_HOME:-}" ]]; then
  REPO_ROOT="$HERMES_AGENT_HOME"
elif [[ -d "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/empire" ]]; then
  # Script is inside the repo — resolve relative to its location
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
else
  echo "[ERROR] Cannot determine repo root. Set HERMES_AGENT_HOME env var." >&2
  exit 1
fi

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
SNAPSHOT_DIR="$OPENCLAW_HOME/memory/archive/snapshots/$(date +%Y%m%d_%H%M%S)"

say() { echo "$1"; }
run() {
  if $DRY_RUN; then
    echo "  [dry-run] $*"
  else
    eval "$@"
  fi
}

say "🧠 Empire memory setup (dry_run=$DRY_RUN, repo=$REPO_ROOT)"
say ""

# ---------------------------------------------------------------------------
# Snapshot — back up all existing files before touching them
# ---------------------------------------------------------------------------
if [[ -d "$OPENCLAW_HOME" ]] && ! $DRY_RUN; then
  mkdir -p "$SNAPSHOT_DIR"
  for f in \
      "$OPENCLAW_HOME/memory/MEMORY.md" \
      "$OPENCLAW_HOME/memory/backlog.json" \
      "$OPENCLAW_HOME/memory/approval-queue.json" \
      "$OPENCLAW_HOME/config/soul.md" \
      "$OPENCLAW_HOME/config/brain.md" \
      "$OPENCLAW_HOME/config/config.yaml" \
      "$OPENCLAW_HOME/config/security.md"; do
    [[ -f "$f" ]] && cp "$f" "$SNAPSHOT_DIR/" && echo "  Backed up: $f"
  done
  say "  Snapshot: $SNAPSHOT_DIR"
fi

# ---------------------------------------------------------------------------
# Create directory structure (always safe — mkdir -p is idempotent)
# ---------------------------------------------------------------------------
run mkdir -p \
  "$OPENCLAW_HOME/memory/"{raw,compressed,daily,archive/snapshots} \
  "$OPENCLAW_HOME/config/playbooks" \
  "$OPENCLAW_HOME/logs/"{audit,security,cost} \
  "$OPENCLAW_HOME/workspace/projects/"{Nathan_CoS,BLCO_Broker,B2B_Outreach,SEO_Content,UGC_Studio,Trading_Bot,Ecommerce,ADAI_INC,CashClaw,51Dynamics}

# ---------------------------------------------------------------------------
# MEMORY.md — create only if it doesn't exist; append a reinstall note otherwise
# ---------------------------------------------------------------------------
MEMORY_FILE="$OPENCLAW_HOME/memory/MEMORY.md"
if [[ ! -f "$MEMORY_FILE" ]]; then
  run "echo '# PERMANENT MEMORY VAULT — ADAI Empire' > '$MEMORY_FILE'"
  run "echo 'Created: \$(date)' >> '$MEMORY_FILE'"
  say "  Created: $MEMORY_FILE"
else
  run "echo '' >> '$MEMORY_FILE'"
  run "echo '# Reinstalled: \$(date)' >> '$MEMORY_FILE'"
  say "  Appended reinstall note: $MEMORY_FILE (existing content preserved)"
fi

# ---------------------------------------------------------------------------
# backlog.json — create only if it doesn't exist
# ---------------------------------------------------------------------------
BACKLOG_FILE="$OPENCLAW_HOME/memory/backlog.json"
if [[ ! -f "$BACKLOG_FILE" ]]; then
  if ! $DRY_RUN; then
    cat > "$BACKLOG_FILE" << 'EOF'
{
  "version": "1.0",
  "priorities": {
    "P0_wealth": [
      {"id": 1, "name": "BLCO_Broker", "status": "pending", "value_scenario": "$700k/deal (unvalidated — treat as target, not forecast)"},
      {"id": 2, "name": "B2B_Outreach", "status": "pending", "value_scenario": "$10k-50k/mo (unvalidated)"},
      {"id": 3, "name": "Trading_Sentinel", "status": "pending", "value_scenario": "$2k-10k/mo (unvalidated)"},
      {"id": 4, "name": "SEO_Content", "status": "pending", "value_scenario": "$2k-10k/mo (unvalidated)"},
      {"id": 5, "name": "UGC_Studio", "status": "pending", "value_scenario": "$1k-5k/mo (unvalidated)"},
      {"id": 6, "name": "CashClaw_Director", "status": "pending", "value_scenario": "$5k-15k/mo (unvalidated)"},
      {"id": 7, "name": "51Dynamics_PetStore", "status": "active", "value_scenario": "$5k/mo (unvalidated)"}
    ],
    "P1_ops": [
      {"id": 8, "name": "Client_Onboarder", "status": "pending"},
      {"id": 9, "name": "Proposal_Writer", "status": "pending"},
      {"id": 10, "name": "Invoice_Manager", "status": "pending"},
      {"id": 11, "name": "Meeting_Summarizer", "status": "pending"},
      {"id": 12, "name": "Contract_Reviewer", "status": "pending"}
    ],
    "P2_personal": [
      {"id": 13, "name": "Morning_Brief", "status": "pending"},
      {"id": 14, "name": "Email_Triager", "status": "pending"},
      {"id": 15, "name": "Second_Brain", "status": "pending"},
      {"id": 16, "name": "Evening_Review", "status": "pending"}
    ]
  }
}
EOF
  else
    echo "  [dry-run] Would create: $BACKLOG_FILE"
  fi
  say "  Created: $BACKLOG_FILE"
else
  say "  Skipped (exists): $BACKLOG_FILE"
fi

# ---------------------------------------------------------------------------
# approval-queue.json — create only if it doesn't exist
# ---------------------------------------------------------------------------
QUEUE_FILE="$OPENCLAW_HOME/memory/approval-queue.json"
if [[ ! -f "$QUEUE_FILE" ]]; then
  if ! $DRY_RUN; then
    cat > "$QUEUE_FILE" << 'EOF'
{
  "queue": [],
  "budget": {"tokens_remaining": 5, "daily_tokens": 5},
  "history": []
}
EOF
  else
    echo "  [dry-run] Would create: $QUEUE_FILE"
  fi
  say "  Created: $QUEUE_FILE"
else
  say "  Skipped (exists): $QUEUE_FILE"
fi

# ---------------------------------------------------------------------------
# Copy config files from repo (overwrites are safe — snapshot taken above)
# ---------------------------------------------------------------------------
copy_config() {
  local src="$1" dst="$2" mode="${3:-644}"
  if [[ -f "$src" ]]; then
    run "cp '$src' '$dst' && chmod $mode '$dst'"
    say "  Installed: $dst"
  else
    say "  [WARN] Source not found, skipping: $src"
  fi
}

copy_config "$REPO_ROOT/empire/soul/SOUL.md"              "$OPENCLAW_HOME/config/soul.md"
copy_config "$REPO_ROOT/empire/soul/BRAIN.md"             "$OPENCLAW_HOME/config/brain.md"
copy_config "$REPO_ROOT/empire/infra/MODEL-ROUTING.yaml"  "$OPENCLAW_HOME/config/config.yaml"
copy_config "$REPO_ROOT/empire/infra/SECURITY.md"         "$OPENCLAW_HOME/config/security.md" 600

# ---------------------------------------------------------------------------
# Post-install validation
# ---------------------------------------------------------------------------
say ""
ERRORS=0
for required in \
    "$OPENCLAW_HOME/memory/MEMORY.md" \
    "$OPENCLAW_HOME/memory/backlog.json" \
    "$OPENCLAW_HOME/memory/approval-queue.json"; do
  if $DRY_RUN; then
    say "  [dry-run] Would verify: $required"
  elif [[ ! -f "$required" ]]; then
    say "  [FAIL] Missing: $required"
    ERRORS=$((ERRORS + 1))
  else
    say "  [OK] $required"
  fi
done

if [[ $ERRORS -gt 0 ]]; then
  say ""
  say "❌ Setup completed with $ERRORS error(s). Snapshot at: $SNAPSHOT_DIR"
  exit 1
fi

say ""
say "✅ Memory system ready ($($DRY_RUN && echo 'dry-run — nothing written' || echo "snapshot at $SNAPSHOT_DIR"))"
say "   Next: run CRON-SETUP.sh to activate scheduling."
