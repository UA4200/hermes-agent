# OpenClaw Free LLM Platform Phase 2 — Workstream 8: Safe Retirement

**Evidence class:** Live_Verified. Per the brief: this workstream
classifies and plans; it does not delete or stop anything. All
dependency-analysis checks below (grep for imports, crontab/launchd
review, real-traffic/log inspection) were run live this session or
carried forward from Phase 1/2 Workstream 1-7 findings, not assumed.

## Two New Components Found This Workstream

Investigating "every candidate component" (not just Phase 1's original
list) surfaced two more parallel, unused routing implementations:

1. **`claude-proxy`** (pm2, port **4099**) — `claude_proxy.py`: *"Lightweight
   Anthropic-compatible proxy → Ollama... for Claude Code to use at $0
   cost. Maps /v1/messages → Ollama qwen2.5:3b."* Structurally
   unreachable: Claude Code's real `ANTHROPIC_BASE_URL` points to port
   **4100** (`oe-proxy`), confirmed in Phase 1's `.zshrc`/`~/.claude/
   settings.json` read — nothing points at 4099.
2. **`fcc_router.py`** — *"FCC Governed Auto-Selector — Open Empire Cost
   Router... Role: Select cheapest passing provider for any given task
   type."* Has its own complete task-chain map and cost table, entirely
   separate from `adaptive_router.py`'s and `ai_router.py`'s. Grepped for
   importers this session (`from fcc_router import` / `import
   fcc_router`) across `~/.openclaw`: **zero results.** Only its own
   file's docstring shows the intended usage — never actually adopted.

This brings the real count of independently-built, never-integrated
routing implementations on this one host to **seven**:
`adaptive_router.py`, `ai_router.py` (the two real, active ones), plus
`model-cost-gateway`, `native-router`, `economic_guard.py`,
`groq_rotator.py`, `claude-proxy`, `fcc_router.py` (six dormant ones —
`economic_guard.py`/`groq_rotator.py` confirmed dormant in Phase 1; the
other four confirmed across Phase 1 and this workstream).

## Classification

| Component | Classification | Dependency analysis |
|---|---|---|
| `adaptive_router.py` | **Retain**, target for **Merge** (Workstream 9) | Real traffic via `oe-proxy`; Workstream 2 already proved `router_core` equivalence for eventual merge |
| `ai_router.py` | **Retain**, target for **Merge** (Workstream 9) | 179,725 real logged calls via `alusi-gateway`; same merge target |
| Free-Way | **Retain** | Healthy, actively used by `adaptive_router.py`, 5+ days uptime, 0 restarts |
| `oe-proxy` | **Retain** | Real entry point for Claude Code CLI |
| Ollama | **Retain** | Real backend for the `local`/`ollama_first` chains |
| `model-cost-gateway` | **Retire** | No cron/launchd reference (Phase 1); ledger is synthetic smoke-test data only, last real-shaped entry 2026-09-16 |
| `native-router` | **Retire** | 5 total events, all from a single day (2026-07-30), none since despite running for 2+ months (Phase 1) |
| `economic_guard.py` | **Retire** | Not imported anywhere, not in any cron entry (Phase 1) |
| `groq_rotator.py` | **Retire** | Same — not imported, not scheduled (Phase 1) |
| `claude-proxy` | **Retire** | Structurally unreachable — nothing points at its port (this workstream) |
| `fcc_router.py` | **Retire** (or **Archive** as a design reference — see below) | Zero importers found anywhere (this workstream) |

**Nothing was classified as "Archive" outright** in the brief's sense of
"keep the code, stop running it" vs. "Retire" (remove entirely) — that
distinction is a judgment call left to you, not decided here. One
exception worth naming: `fcc_router.py`'s task-chain design (cheapest-
first with an explicit-escalation gate before Sonnet/Opus) is
conceptually similar to what `router_core`'s policy layer already does —
worth a read before deletion in case its specific chain tuning has
insight `router_core`'s current (illustrative, Workstream 5) defaults
don't, even though the module itself is never called.

## Recommended Order of Operations (Not Executed — Plan Only)

1. **Stop, don't delete, first.** `pm2 stop` each of the 6 retirement
   candidates (a one-command, instantly-reversible `pm2 restart` away)
   and observe for a defined period (propose: 1 week) — if truly
   unreachable/unused, nothing should notice.
2. **Then remove from pm2's saved process list** (`pm2 delete` +
   `pm2 save`) once the observation period confirms no regression.
3. **Only then consider deleting the code itself** — and even then,
   per the brief's "Archive" option, a simple `git`-tracked move to an
   `archive/` directory preserves the design reference (relevant for
   `fcc_router.py` specifically) without it running.
4. **`model-cost-gateway`'s launchd plist** should be explicitly
   confirmed still unloaded (`launchctl list | grep openempire` — empty,
   per Phase 1) before any of the above, so retirement isn't undone by a
   forgotten scheduled job reactivating it.

## Why Not Executed This Workstream

The brief is explicit: *"Delete nothing until dependency analysis
confirms safety."* Dependency analysis is now complete and consistently
finds zero live dependents for all 6 candidates — but "confirms safety"
and "therefore execute" are two different steps, and this workstream's
own deliverable is the plan, not the action. Workstream 10 (Prioritized
Remediation) or a direct follow-up request from you are the right places
to actually execute step 1 above, now that write access has been granted
for this session.
