# OpenClaw Free LLM Platform Phase 2 — Workstream 5: Client Toolchain

**Evidence class:** Live_Verified, real resource measurements this
session.

## Resource Measurements (Real, Not Estimated)

| Metric | Value | Source |
|---|---|---|
| Total system RAM | 16GB (`sysctl hw.memsize` = 17,179,869,184 bytes) | Live check |
| VS Code memory footprint | **~547MB across 8 processes** | `ps aux`, live sum |
| Codex CLI memory footprint | **~300MB+ across 9 processes** (multiple concurrent instances — 4 separate `codex` binaries plus `node` helpers, each ~25-83MB) | `ps aux`, live sum |
| Free memory | **~248MB** (63,629 pages × 4096 bytes) | `vm_stat`, live check |
| Reclaimable (inactive) memory | ~5.6GB (1,437,311 pages) | `vm_stat`, live check |

## VS Code: Deferred, Per the Brief's Own Conditional

VS Code is installed and currently running (`Visual Studio Code.app`
confirmed present). Its own footprint (~547MB, ~3.4% of total RAM) is not
dramatically excessive in isolation — but the system as a whole is
running with genuinely low free memory (~248MB) on old, weak, dual-core
hardware, with multiple concurrent Codex CLI instances already
contributing real load. **Judgment call, stated as such, not a hard
threshold the brief defined**: given this real resource picture, active
VS Code *routing* integration (wiring it into `router_core`, adding
extension-host processes) is deferred per the brief's own explicit
instruction — not because VS Code itself measured as excessive, but
because the honest margin for adding more concurrent process load on
this specific machine is thin right now. Revisit after Workstream 9's
deployment proves the core consolidation doesn't add further pressure.

## Per-Tool Configuration Status

| Tool | Status | This workstream's action |
|---|---|---|
| Claude Code | Already configured (`ANTHROPIC_BASE_URL` → `oe-proxy`, Phase 1) | No change — already correctly wired |
| Codex CLI | Installed, actively used, **not routed** (Workstream 3) | Design-only per Workstream 4's decision — not touched live, a tool someone is using right now |
| "Hermes" | N/A — no separate CLI on this host (Workstream 3) | No action needed |
| OpenClaw Free LLM Platform | This is what `router_core` (Workstream 2/4) *is* | Built, tested, not deployed — Workstream 9 |
| EOS Runtime | **N/A to this host.** `engineering-operating-system`'s Runtime is a component of a different repository entirely (established Phase 1, `AI_ORCHESTRATION_CAPABILITY.md`) — `ugos-mac-mini` does not run it and this program does not introduce it there | No action — out of scope by definition, not by oversight |

## What Was Not Done

No live configuration was changed for any tool. VS Code was not touched
(not installed, not modified, not integrated). Codex's `config.toml` was
read (Workstream 3) but not edited. This workstream's job was measurement
and a scoped deferral decision, not live reconfiguration — consistent
with every prior workstream's discipline on this specific live host.
