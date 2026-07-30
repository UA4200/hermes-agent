# 01_PM2_PROCESS_MAP — Live Process Evidence
**Generated:** 2026-07-30  
**Source:** Terminal screenshot from `neoOC@ugos-mac-mini`  
**Evidence class:** LOCAL_VERIFIED

---

## PM2 PROCESS LIST

| # | Name | Status | Restarts | Memory | Notes |
|---|---|---|---|---|---|
| 1 | alusi-gateway | 🟢 online | 2 | 26.9mb | Minor restarts |
| 5 | alusi-orchestrator | 🟢 online | 0 | 6.9mb | Stable |
| 2 | alusi-telegram-ad... | 🟢 online | 0 | 21.6mb | Telegram admin |
| 16 | blco-daily-sourcer | 🔴 **stopped** | — | — | ⚠️ Needs restart |
| 15 | blco-email-monitor | 🟢 online | 0 | 7.8mb | Stable |
| — | blco-enricher | 🟢 online | 0 | 8.6mb | Stable |
| 1 | cashclaw | 🔴 **stopped** | — | — | ⚠️ Needs restart |
| 6 | cashclaw_director | 🟢 online | 2 | 9.9mb | Minor restarts |
| 7 | cost-dashboard | 🟢 online | 0 | 5.4mb | Stable |
| 22 | ecosystem.email-d... | 🟢 online | 0 | 46.4mb | Email dispatcher |
| 18 | exec-gateway | 🟢 online | 0 | 6.7mb | Stable |
| 9 | executor | 🟢 online | 0 | 51.1mb | Stable |
| 22 | heartbeat | 🟢 online | 0 | 9.3mb | Stable |
| 30 | hyrve-monitor-v2 | 🟢 online | 0 | 50.3mb | Stable |
| 29 | mission-control | 🟢 online | 0 | 44.2mb | Stable |
| 32 | n8n | 🟢 online | 0 | 92.3mb | Highest memory |
| 23 | nexus-dashboard | 🟢 online | 0 | 9.0mb | Stable |
| 35 | nexus-telemetry | 🟢 online | 0 | 43.3mb | Stable |
| 21 | open-empire-Contr... | 🟢 online | 0 | 33.3mb | Stable |
| 25 | **open-empire-missi...** | 🟢 online | **113** | 5.7mb | 🚨 CRASH LOOP |
| 28 | open-empire-nexus | 🟢 online | 0 | 35.9mb | Stable |
| 24 | openclaw-audit | 🔴 **stopped** | — | 16.9mb | ⚠️ Needs restart |
| — | pnl-sync | 🟢 online | 0 | — | Stable |
| 3 | skill-sync | 🟢 online | 0 | — | Stable |
| 11 | telegram-approvals | 🟢 online | 0 | 9.6mb | Stable |
| 14 | trading_sentinel | 🟢 online | 0 | 19.7mb | Stable |

**Total processes:** ~27 managed by pm2

---

## 🚨 CRITICAL: open-empire-missi... — 113 RESTARTS

This process is in a crash loop. pm2 keeps restarting it; it dies immediately each cycle.

**Diagnose immediately:**
```bash
pm2 logs open-empire-missi... --lines 50 --nostream
pm2 describe open-empire-missi...
```

Likely causes:
- Missing env var / secret it expects at startup
- Port conflict with another process
- Python import error (missing dependency)
- File it reads at startup has been deleted/moved

**Do NOT** restart or restart pm2 globally until the crash cause is identified — 113 restarts means it's been looping for hours and a blind restart won't fix it.

---

## STOPPED PROCESSES (3)

| Process | Action |
|---|---|
| `blco-daily-sourcer` | Check logs before restarting: `pm2 logs blco-daily-sourcer --nostream --lines 30` |
| `cashclaw` | Check logs: `pm2 logs cashclaw --nostream --lines 30` |
| `openclaw-audit` | Check logs: `pm2 logs openclaw-audit --nostream --lines 30` |

---

## PORT LISTENERS (lsof output)

| PID | User | Command | Address | Port | State |
|---|---|---|---|---|---|
| 3639 | NeoOC | python | 127.0.0.1 | :808 | — |
| 3643 | NeoOC | python | 127.0.0.1 | :444 | — |
| 3682 | NeoOC | python | 127.0.0.1 | :889 | — |
| 3687 | NeoOC | python | 127.0.0.1 | :879 | — |
| 3691 | NeoOC | python | 127.0.0.1 | :879 | — |
| 3767 | NeoOC | python | 127.0.0.1 | :879 | — |
| 3767 | NeoOC | python | * | :4445 | LISTEN |
| 4926 | NeoOC | node | * | :4445 | LISTEN |
| 4293 | NeoOC | node | * | :11333 | — |
| 2694 | NeoOC | node | * | :14444 | LISTEN |
| 2694 | NeoOC | node | [::1] | :11878 | LISTEN |
| 97711 | NeoOC | node | * | :6478 | LISTEN |

**Port notes:**
- Port `:4445` has BOTH a python and a node process — potential conflict
- `:14444` = likely nexus-dashboard or mission-control API
- `:6478` = likely n8n or openclaw API
- `:879` has multiple python processes — intentional fan-out or collision?
- `:11878` = local only ([::1]) — likely internal IPC

---

## ACTIVE EXTERNAL SESSIONS (visible in screen top-right)

- **Telegram:** Multiple sessions active (`telegram:@...`, `telegram:g...`)
- **Discord:** Session active (`discord:1500`)

This confirms Telegram and Discord bots are live and receiving messages.

---

## OPEN-EMPIRE-ROS DISCOVERY

`open-empire-nexus` (running, 35.9mb) and `open-empire-Contr...` and `open-empire-missi...` are all running — these are the **open-empire-ros runtime processes**. The repo may live under a different path than `~/open-empire-ros`.

**Find it:**
```bash
pm2 describe open-empire-nexus | grep -E "script|cwd|exec"
pm2 describe open-empire-missi... | grep -E "script|cwd|exec"
```

This will reveal the actual path of the open-empire-ros codebase on disk.

---

## PHASE 1 SUMMARY

| Category | Count | Status |
|---|---|---|
| pm2 processes total | ~27 | Running |
| Online | ~23 | Healthy |
| Stopped | 3 | Need investigation |
| **Crash-looping** | **1** | **🚨 P0 — fix now** |
| Port listeners | 12 | One conflict on :4445 |

**P0 action:** `pm2 logs open-empire-missi... --lines 50 --nostream` — identify and fix the crash root cause before any other infrastructure work.
