# OpenClaw Free LLM Platform — Final Report (Workstream 11)

**Program:** OpenClaw Free LLM Platform, Client 001 – Alusi.
**Date:** 2026-09-22. **Repository:** `hermes-agent`, branch
`claude/openclaw-freellm-platform`, 10 commits + 1 correction commit.

---

## FINAL VERDICT

# READY WITH CONDITIONS

---

## Why Not READY FOR CLIENT DEPLOYMENT

Two real, currently-open gaps, both independently verified this program
(not assumed):

1. **Cost-limit enforcement is a confirmed gap in one system
   (`ai_router.py`) and a genuinely unverified question in another
   (`oe-proxy`)** — real money is downstream of this (the `cashclaw`
   chain routes to Opus/Sonnet), even though real usage to date has never
   actually reached those tiers (Workstream 6/7).
2. **The one automated safety mechanism that exists to catch and remediate
   exactly this class of problem — `empire_efficiency.py`'s hourly canary
   + auto-rollback — is itself broken** (a PATH/node bug crashes the
   rollback before it completes, Workstream 7), so the gap above has had
   no working automatic backstop for an unknown period.

Neither of these was fixed by this program — both are real, specific,
low-risk-to-fix items held for your explicit approval, per this program's
running discipline of not modifying live production infrastructure
unasked.

## Why Not NOT READY

The overwhelming majority of what this program found is real, working
infrastructure, not a system that needs to be built from scratch — which
was the brief's original (incorrect) premise:

- Two independent, real routing systems handling 179,725+ real production
  calls (Workstream 1/2).
- Free-Way: healthy, actively used, zero restarts in 5+ days (Workstream
  2/7).
- Real, live trading workflows actively finding opportunities (Workstream
  8) — currently funding-constrained, not code-broken.
- An existing, thoughtful, already-scheduled self-governance system
  (`empire_efficiency.py`) that this program used rather than duplicated.
- Four processes a prior report flagged as crash-looping are confirmed
  working exactly as designed (Workstream 1/2).

A "NOT READY" verdict would misrepresent a system that is, for the most
part, already working.

## Conditions for READY FOR CLIENT DEPLOYMENT

In priority order:

1. Determine whether `oe-proxy` actually enforces a cost limit (the
   canary test that was supposed to answer this is stale — Workstream 7)
   — this is the single highest-value open question, since the answer
   determines whether items 2-3 are urgent or already covered.
2. Implement the missing enforcement in `ai_router.py` (or, longer-term,
   in a consolidated `router_core`-based replacement) per Workstream 6's
   specific recommendation.
3. Fix `empire_efficiency.py`'s rollback PATH bug (Workstream 7) — small,
   isolated, mirrors a fix already applied elsewhere in the same crontab
   today.
4. Rotate the Gemini API key found exposed in `native-router`'s log
   (Workstream 2) — independent of everything else, shouldn't wait.
5. Decide on and execute the Postgres role fix or dead-code removal
   (Workstream 4) — lower priority, no current impact (JSONL fallback
   works), but real technical debt.

None of these require the larger router consolidation
(`OPENCLAW_PLATFORM_ARCHITECTURE.md`'s staged migration) to be resolved
first — they're independent, faster wins.

## EOS Integration — What Would Be Captured, Not Yet Captured

The brief asks to update `engineering-operating-system`'s Engineering
Memory, Capability Registry, Provider Registry, and Knowledge Graph. This
program deliberately did not write to that repository:
`engineering-operating-system` has its own governance (encountered during
the related EL-003 program) — capability promotion is a Chief-Architect-
level decision gated on 8 promotion criteria, not something a single
program's final report performs unilaterally, especially for a
prototype (`router_core`) with no production mileage yet.

**What a future, approved promotion would capture:**
- **Capability Registry:** `router_core` as a candidate AI Orchestration
  capability, status "prototype — tested, not deployed" (per Workstream
  9's honest per-responsibility status table).
- **Provider Registry:** Free-Way, Ollama, and the direct Anthropic/OpenAI
  paths as provider entries, if this pattern generalizes beyond this one
  empire.
- **Engineering Memory / Patterns:** the "two independently-built
  orchestration systems, never merged" root-cause pattern (Workstream 2)
  is a reusable lesson — worth capturing generically ("check for parallel
  implementations before building new infrastructure") independent of
  this specific system.
- **Knowledge Graph:** not evaluated for a connection point this pass.

**Reusable vs. client-specific, separated explicitly:**

| Reusable (candidate for future EOS capture) | Client-specific (Alusi/`ugos-mac-mini`-only) |
|---|---|
| `router_core`'s design pattern (policy + engine + cache/compress hooks) | `model_policy.json`'s actual task-type mappings and cost limits |
| The "check for parallel routing implementations" root-cause lesson | The specific fact that Free-Way is on port 8082 here |
| `install_check.py`'s verify-before-trust pattern | The specific pm2 process names/ports on this host |
| The circuit-breaker/scoring shape (independent of tuned weights) | `adaptive_router.py`'s actual tuned weights and provider catalog |

## Full Deliverable Index

| Workstream | Deliverable | Real content? |
|---|---|---|
| 1 | `CURRENT_AI_ENVIRONMENT.md` | Live SSH investigation |
| 2 | `ROOT_CAUSE_ANALYSIS.md` | Live-verified, corrects the brief's premise |
| 3 | `FREE_LLM_ECOSYSTEM_REVIEW.md` + `CACHING_AND_ACCELERATION_RESEARCH.md` | Sourced research, GitHub-API-verified maintenance status |
| 4 | `OPENCLAW_PLATFORM_ARCHITECTURE.md` | Proposal, not executed |
| 5 | `MODEL_ROUTING_POLICY.md` + `router_core/` | Real, tested (18/18) code |
| 6 | `TOKEN_OPTIMIZATION_REPORT.md` | Live-verified, real cost figures |
| 7 | `FREEWAY_LLM_REBUILD.md` (+ correction commit) | Live-verified, self-corrected finding |
| 8 | `CLIENT_ACCEPTANCE_REPORT.md` | Live-verified, honest per-dimension status |
| 9 | 4x `AI_ORCHESTRATION_*.md` + `install_check.py` | Real, runnable installer |
| 10 | 3x `OPENCLAW_*`/`OPENCLAW_PLATFORM_*.md` | Honest v0.1.0-prototype packaging |
| 11 | This document | — |

## Constraint Compliance

- Did not replace working client functionality without evidence — no
  client functionality was replaced at all.
- Did not introduce vendor lock-in — `router_core` has zero required
  dependencies; no paid-only service was proposed.
- Did not invent benchmark results — every number in this program traces
  to a live command run this session, with two documented self-corrections
  (Workstream 7's overstated finding, Workstream 5's test bugs) where a
  first pass got something wrong and it was caught and fixed rather than
  left standing.
- Did not reduce engineering governance — proposed *adding* enforcement
  where it was found missing, never removing an existing check.
- Did not duplicate orchestration logic across products — the opposite:
  found existing duplication (Workstream 2) and designed, but did not yet
  execute, its consolidation.
