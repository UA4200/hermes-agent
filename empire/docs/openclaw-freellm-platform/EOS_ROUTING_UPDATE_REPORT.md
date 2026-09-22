# OpenClaw Free LLM Platform Phase 2 — Workstream 11: EOS Capability Update

**Same governance stance as Phase 1, not repeated by default:**
`engineering-operating-system`'s Capability/Provider Registries and
Engineering Memory are a different repository with its own promotion
gate (8 criteria, Chief-Architect-level decision). This workstream
documents what this phase adds to that eventual case — it does not write
to that repository.

## What Changed Since Phase 1's Equivalent Report

Phase 1's `FINAL_PRODUCT_REPORT.md` already laid out the
reusable-vs-client-specific split for `router_core`. Phase 2 adds real
production mileage that changes the maturity assessment:

| Then (Phase 1) | Now (Phase 2) |
|---|---|
| `router_core`: 18 tests, illustrative example data | 61 tests, real ported production data (catalog, policy, classification), proven equivalence to both live systems |
| Deployed: nowhere | Deployed to an isolated staging directory on the live host, 61/61 passing in the real target runtime (Python 3.14.6) |
| Cost enforcement: identified as a gap | Built, tested twice (unit + real integration), staged for the actual live file |
| Safety backstop: identified as broken | **Fixed and demonstrated working on the live host**, real evidence not simulated |

## New Reusable Patterns This Phase Surfaced

1. **"Audit for duplicate infrastructure" needs to be exhaustive, not a
   single pass.** Phase 1 found 5 dormant routing implementations; this
   phase's Workstream 8, explicitly re-investigating "every candidate
   component" rather than trusting the prior list, found 2 more
   (`claude-proxy`, `fcc_router.py`) — bringing the real total to 7. The
   reusable lesson isn't "there were 7 duplicates," it's "a first
   dependency-analysis pass finding N instances doesn't mean N is the
   real count — re-run it from scratch, don't extend the prior list."
2. **A tiered live-write permission model is a real, valuable safety
   pattern, observed in practice this session**, not designed in the
   abstract: distinct classifiers fired for "remote shell writes"
   (crontab edit), "production deploy" (replacing a live routing file),
   and "secret-store writes" (reading a credential into a command) — each
   independently grantable, none implying the others. Worth capturing as
   a pattern for any future EOS capability that touches live client
   infrastructure: **scope permission grants to the specific action
   class, not the whole session**, and expect a tool/agent to hit
   several distinct gates on a single program, not one.
3. **Verify a fix using the exact environment it will run in, not an
   approximation.** Workstream 7's fix was verified using cron's actual
   minimal `PATH`, not a "close enough" simulation — and an earlier,
   looser attempt at this (`env -i` stripping too much) produced a
   misleading hang rather than a clean result. The specific lesson:
   simulate the *minimum necessary* difference from your own environment
   (just `PATH`, here), not a maximal one (`env -i`, which strips things
   unrelated to the actual bug and can introduce new, confusing failure
   modes).
4. **Check a tool's raw output, not its own summary field, before
   trusting a finding.** Reinforced twice this phase: Workstream 7's
   correction commit (Phase 1) and Workstream 10's `oe-proxy` cost-gate
   discovery both came from reading actual HTTP responses / actual source
   code rather than accepting a prior summary at face value.

## Reusable vs. Client-Specific (Updated Split)

| Reusable (candidate for future EOS capture) | Client-specific (Alusi/`ugos-mac-mini`-only) |
|---|---|
| `router_core`'s full design, now with 61 real tests | The real `alusi_model_policy.json` fixture's actual cost/chain values |
| The 4 patterns above | The specific fact that `oe-proxy` enforces a $0.05 ceiling (the *mechanism* — "cost-limit-then-approval-gate before any paid tool-use" — is the reusable part; the dollar figure is this deployment's tuning) |
| `install_check.py`'s verify-before-trust pattern | `ai_router.py`'s specific patched diff (the *pattern* — policy-declared limits should be checked in code, not just documented — is reusable; the diff itself is this file's) |
| The Engineering-Lab-style "stage before deploy, gate before cutover" workflow this whole phase followed | Every specific port number, process name, and pm2 process list found this session |

## Not Done

No write to `engineering-operating-system`'s registries, Knowledge Graph,
or Engineering Memory. No capability promotion decision made — that
remains, as in Phase 1, a decision for you or a governed program in that
repository, not this one.
