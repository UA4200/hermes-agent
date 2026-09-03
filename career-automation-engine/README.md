# Career Automation Engine

Playwright + Google Sheets job-application automation with a human
approval gate, built from Nathan's handoff package (`README_AUTOMATION_PACKAGE.md`,
`CLAUDE_CODE_HANDOFF.md`, `SETUP.md`, `IMPLEMENTATION_CHECKLIST.md`,
`JOB_BOARDS.md`).

## Status: code complete, NOT run or verified yet

This was built and pushed from a cloud Claude Code session, which cannot
run the actual system — there's no local browser, no persistent server
reachable at `localhost:3000`, and no real credentials (Claude API key,
Google service account, Indeed session cookie) available to it. Every
file below exists and is internally consistent, but **Phases 2–4 of
`IMPLEMENTATION_CHECKLIST.md` (scoring, dashboard, end-to-end submit)
have not been executed against a live target.** Run it yourself per
"Run it" below, and treat the first cycle as a real test, not a
formality — some ATS forms will need selector tweaks in
`src/automation/playwright-automation.js` that no amount of code review
substitutes for.

## Real risk you're accepting

Auto-filling and auto-submitting applications via Playwright against
Indeed and (if enabled) LinkedIn conflicts with those platforms'
Terms of Service, and their anti-bot detection can flag or suspend the
account whose session cookie you use — independent of the human
approval step. You told Claude Code to build the full pipeline anyway;
this is not hidden by the approval gate, just noted here so it stays
visible. LinkedIn scraping ships **off by default** — enable explicitly
with `--include-linkedin` in `fetch-job-boards.py`.

## What's different from the original spec, and why

- **`.env` instead of `CONFIG.json`.** Secrets in a `.json` file in a
  git repo are one `git add .` away from a leak; `.env` is gitignored
  by default across this whole toolchain.
- **Google service account instead of a bare API key.** A plain Sheets
  API key is read-only for public sheets — it cannot write the status
  updates this system makes constantly. See `SETUP.md` step 2.
- **Cross-process state via `state/current-job.json`.** The original
  pseudocode had `dashboard-server.js` and `job-processor.js` share an
  in-memory `currentJob` variable, but `SETUP.md` runs them as two
  separate `node` processes — plain JS variables don't cross process
  boundaries. A small state file is the fix; `dashboard-server.js`
  never touches Playwright directly, only `job-processor.js` (which
  owns the browser) does.

## Run it (on your own machine, not a cloud session)

```bash
cd career-automation-engine
npm install
pip install -r requirements.txt
cp .env.example .env        # fill in real values — see SETUP.md
node src/scripts/validate-config.js

python3 src/scripts/fetch-job-boards.py --source indeed --limit 18
python3 src/scripts/score-jobs.py --input data/jobs_discovered.json

bash start-automation.sh
# open http://localhost:3000
```

See `SETUP.md` for credential setup and `IMPLEMENTATION_CHECKLIST.md`
for the full phase-by-phase validation checklist — follow it for real;
none of those checks have been ticked yet.

## Layout

```
src/
  dashboard-server.js       Express app: /api/status, /api/approve, /api/reject, /api/log
  dashboard/index.html      Approval UI (polls /api/status every 2s)
  automation/
    job-processor.js        Owns the Playwright browser; drives the approval loop
    playwright-automation.js  Field detection/fill, screenshots, submit, confirmation capture
  scripts/
    fetch-job-boards.py     Indeed (Selenium+cookie), RemoteOK/JustJoinIT/WWR (public APIs), LinkedIn (opt-in)
    score-jobs.py            Claude API fit scoring -> Sheets
    sheets_client.py         Python Sheets read/append/update
    validate-config.js       Preflight credential/connectivity checks
  lib/
    config.js, logger.js, state.js, sheets.js   Node-side shared helpers
```

## Tracker columns (Google Sheet)

`A: Company | B: Role | C: Source | D: URL | E: Posted | F: Salary |
G: Fit Score | H: Resume Used | I: Form Type | J: Status | K: Submitted
Date | L: Confirmation # | M: Next Action`

Status flows: `SCORED → FORM_FILLED → SUBMITTED` (or `REJECTED` /
`ERROR`).
