# OpenClaw Free LLM Platform Phase 2 — Workstream 7: Automated Safety

**Evidence class:** Live_Verified diagnosis, fix prepared and verified as
a clean diff, **not applied** — blocked by this session's own tool
permission system, not by any finding that the fix is unsafe. Held for
your explicit action per the note at the end of this document.

## Scope Expanded — A Real Finding Beyond Phase 1's Original Diagnosis

Phase 1 found `canary --rollback-on-critical`'s hourly cron entry
crash-looping on a PATH/node issue. This workstream checked whether the
same bug affects other `empire_efficiency.py` cron entries, rather than
assuming it's isolated:

| Cron entry | Calls `pm2_list()`/`pm2 restart`? | Affected? |
|---|---|---|
| `canary --rollback-on-critical` (hourly) | Yes (`rollback_proxy()`) | **Yes — confirmed, Phase 1** |
| `env-audit` (daily, 4:27am) | Yes (`env_audit()` → `pm2_list()`) | **Yes — confirmed this session**: `reports/pm2-env-audit.json` has not been updated in **7 days** (last write 2026-09-15) despite running daily |
| `dashboard` (daily, 4:32am) | No — HTTP health checks only | Not affected |
| `qualify --benchmark` (weekly) | No — Ollama HTTP calls only | Not affected |
| `maintenance` (weekly) | Yes (`maintenance()` → `pm2_list()`) | **Yes — same root cause**, not yet independently confirmed via a stale-report check (its report file wasn't inspected for staleness this session) but shares the identical code path |

**Root cause, confirmed precisely**: `pm2` is a Node.js shebang script
(`#!/usr/bin/env node`); cron's minimal environment doesn't have `node`
on `PATH`; `/usr/local/bin/node` (240MB, confirmed present) would resolve
it if `/usr/local/bin` were on cron's `PATH`, which it isn't by default.

## The Fix — Prepared, Verified, Not Applied

The exact fix pattern already proven working on this host: a separate
cron entry (`pm2 save --force`) was fixed today with a
`PATH="/usr/local/bin:$PATH"` prefix — confirmed genuinely working by
reading its own log (`~/.openclaw/logs/pm2_save.log` shows repeated
`[PM2] Successfully saved` entries). The same prefix, applied to the 3
affected entries, was prepared and diffed clean (exactly 3 lines
changed, nothing else touched):

```diff
- 17 * * * * /usr/local/bin/python3 .../empire_efficiency.py canary --rollback-on-critical >> ...
+ 17 * * * * PATH="/usr/local/bin:$PATH" /usr/local/bin/python3 .../empire_efficiency.py canary --rollback-on-critical >> ...

- 27 4 * * * /usr/local/bin/python3 .../empire_efficiency.py env-audit >> ...
+ 27 4 * * * PATH="/usr/local/bin:$PATH" /usr/local/bin/python3 .../empire_efficiency.py env-audit >> ...

- 52 4 * * 0 /usr/local/bin/python3 .../empire_efficiency.py maintenance >> ...
+ 52 4 * * 0 PATH="/usr/local/bin:$PATH" /usr/local/bin/python3 .../empire_efficiency.py maintenance >> ...
```

A full crontab backup was taken before attempting the change
(`/tmp/crontab_backup_before_ws7.txt`, 87 lines, this session).

## Blocked — Not by Risk Assessment, by This Session's Own Permission Gate

Installing the fixed crontab (`crontab /tmp/crontab_fixed_ws7.txt` on the
live host) was **denied by this session's own tool-permission classifier**
("Remote Shell Writes"), independent of this program's own risk analysis.
This is a real, separate safety layer working as designed — this document
does not attempt to route around it. **The fix is ready; it was not
applied; "demonstrate successful operation" could not be completed this
session as a result.**

## What You'd Need to Do to Apply This

Either:
1. Grant this session permission for remote shell writes and ask it to
   retry, or
2. Apply it yourself:
   ```bash
   ssh NeoOC@100.125.170.39 'crontab -l' > crontab_backup_$(date +%Y%m%d).txt
   # then edit the 3 lines above (add the PATH= prefix) and:
   ssh NeoOC@100.125.170.39 'crontab -' < crontab_fixed.txt
   ```
3. Verify afterward by manually triggering one cycle and checking
   `~/.openclaw/empire/efficiency/reports/scheduler.log` for a clean run,
   or waiting for the next natural hourly `canary` firing.

## Other Items From Phase 1's List (Verified/Repaired State)

| Item | Status |
|---|---|
| Failure detection | Working — `canary`'s checks correctly detect the `paid_cost_gate` issue (Phase 1's corrected finding: stale probe, not a real breach) |
| Router recovery | `router_core`'s `RouterState` circuit-breaker recovery is real and tested (Workstream 2, this phase) — not yet live |
| Provider recovery | Same — tested in `router_core`, not yet live |
| Health monitoring | Working — `dashboard`'s HTTP checks are real and unaffected by the PATH bug |
| Automatic alerts | **Not found anywhere** in `empire_efficiency.py` — failures are logged to `scheduler.log`, nothing pages or notifies. A real gap, not previously stated this plainly: the "automatic alerts" the brief asks to verify **do not exist** on this host today. |
| Automatic rollback | Broken (this document's main finding) — fix prepared, not applied |

## Honest Bottom Line

This workstream diagnosed more precisely than Phase 1 (2 more affected
cron entries found), prepared a verified-clean fix using this exact
host's own proven pattern, and was stopped by a legitimate, separate
safety control before applying it. Nothing was left half-done on the live
host — the backup exists, the fix exists, neither was partially applied.
