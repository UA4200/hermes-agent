# OpenClaw Free LLM Platform — Workstream 10: Installer

The platform installer **is** `empire/router_core/install_check.py` — see
`AI_ORCHESTRATION_INSTALLER.md` for the full walkthrough and real session
output. Not duplicated here; this document exists only to satisfy the
brief's separate deliverable naming, and to note one packaging decision:

**No separate "OpenClaw Free LLM Platform" installer was built distinct
from `router_core`'s own**, because there is nothing else to install —
this program produced one real artifact (`router_core`) plus
documentation. A future program that actually deploys this to
`ugos-mac-mini` (per the staged migration plan) would need a *real*
deployment installer at that point — one that handles pm2 registration,
credential wiring, and the cutover sequencing `OPENCLAW_PLATFORM_
ARCHITECTURE.md` describes. That installer doesn't exist yet because that
deployment hasn't happened yet, consistent with this program's
"proposal, not executed" stance throughout.
