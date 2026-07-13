#!/bin/bash
# MEMORY SYSTEM SETUP — Run once on Mac Mini
# Creates the persistent brain structure for the empire

echo "🧠 Creating empire memory system..."

mkdir -p ~/.openclaw/memory/{raw,compressed,daily,archive}
mkdir -p ~/.openclaw/config/playbooks
mkdir -p ~/.openclaw/logs/{audit,security,cost}
mkdir -p ~/.openclaw/workspace/projects/{Nathan_CoS,BLCO_Broker,B2B_Outreach,SEO_Content,UGC_Studio,Trading_Bot,Ecommerce,ADAI_INC,CashClaw,51Dynamics}

echo "# PERMANENT MEMORY VAULT — ADAI Empire" > ~/.openclaw/memory/MEMORY.md
echo "Created: $(date)" >> ~/.openclaw/memory/MEMORY.md

cat > ~/.openclaw/memory/backlog.json << 'EOF'
{
  "version": "1.0",
  "priorities": {
    "P0_wealth": [
      {"id": 1, "name": "BLCO_Broker", "status": "pending", "value": "$700k/deal"},
      {"id": 2, "name": "B2B_Outreach", "status": "pending", "value": "$10k-50k/mo"},
      {"id": 3, "name": "Trading_Sentinel", "status": "pending", "value": "$2k-10k/mo"},
      {"id": 4, "name": "SEO_Content", "status": "pending", "value": "$2k-10k/mo"},
      {"id": 5, "name": "UGC_Studio", "status": "pending", "value": "$1k-5k/mo"},
      {"id": 6, "name": "CashClaw_Director", "status": "pending", "value": "$5k-15k/mo"},
      {"id": 7, "name": "51Dynamics_PetStore", "status": "active", "value": "$5k/mo"}
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

cat > ~/.openclaw/memory/approval-queue.json << 'EOF'
{
  "queue": [],
  "budget": {"tokens_remaining": 5, "daily_tokens": 5},
  "history": []
}
EOF

echo "✅ Memory system created"
echo "✅ Backlog loaded: 16 use cases"
echo "✅ Approval queue ready"

# Copy config files from repo
cp ~/hermes-agent/empire/soul/SOUL.md ~/.openclaw/config/soul.md
cp ~/hermes-agent/empire/soul/BRAIN.md ~/.openclaw/config/brain.md
cp ~/hermes-agent/empire/infra/MODEL-ROUTING.yaml ~/.openclaw/config/config.yaml
cp ~/hermes-agent/empire/infra/SECURITY.md ~/.openclaw/config/security.md
chmod 600 ~/.openclaw/config/security.md

echo "✅ Soul, Brain, Security, Routing configs installed"
echo ""
echo "🚀 Memory system ready. Run CRON-SETUP.sh next."
