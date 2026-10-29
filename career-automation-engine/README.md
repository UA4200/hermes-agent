# Career Automation Engine

Playwright job-application automation with a human approval gate,
built from Nathan's handoff package (`README_AUTOMATION_PACKAGE.md`,
`CLAUDE_CODE_HANDOFF.md`, `SETUP.md`, `IMPLEMENTATION_CHECKLIST.md`,
`JOB_BOARDS.md`).

Tracker: a plain CSV file (`TRACKER_PATH` in `.env`, defaults to
`data/tracker.csv`) — point it at a folder Google Drive for Desktop
syncs and the tracker shows up in Drive/your phone with zero API setup.
This has gone through two earlier backends (Google Sheets, then
Notion) before landing here — see below for why each got replaced.

## Status: code complete, NOT run or verified yet

This was built and pushed from a cloud Claude Code session, which cannot
run the actual system — there's no local browser, no persistent server
reachable at `localhost:3000`, and no real credentials (Claude API key,
Indeed session cookie) available to it. Every file below exists and is internally consistent, but **Phases 2–4 of
`IMPLEMENTATION_CHECKLIST.md` (scoring, dashboard, end-to-end submit)
have not been executed against a live target.** Run it yourself per
"Run it" below, and treat the first cycle as a real test, not a
formality — some ATS forms will need selector tweaks in
`src/automation/playwright-automation.js` that no amount of code review
substitutes for.

The `--source hackernews` discovery path (added later, via crawl4ai) has
a bit more verification behind it than the rest: the exact crawl4ai
0.9.3 API this code calls (`AsyncWebCrawler`, `CrawlerRunConfig`,
`BrowserConfig`) was checked against a real install via
`inspect.signature`, `requirements.txt` was confirmed to install cleanly
in a fresh venv (crawl4ai needs `aiohttp>=3.11.11`, which the original
pin of `3.10.5` conflicted with — bumped it), and the Python syntax
compiles. What's **not** verified: an actual live run. This sandbox's
network egress doesn't allow `hn.algolia.com` or the Chrome-for-Testing
CDN crawl4ai's browser needs, so the HN thread lookup and the crawl
itself have not been executed end-to-end here — that needs your machine
too.

The tracker backend has moved twice since this was first built — Google
Sheets, then Notion, now a plain CSV file — each time per Nathan's
direction, each time to cut setup friction (a Google Cloud service
account, then a Notion integration token, now nothing at all). The CSV
client (`src/lib/tracker.js` / `src/scripts/tracker_csv.py`) is plain
file I/O with no external dependency, so there's nothing to
authenticate and little that can go wrong beyond a bad path — run
`validate-config.js` to confirm `TRACKER_PATH` is writable. Both the
Node and Python clients were exercised directly in this session
(`validate-config.js`'s connectivity check actually creates and reads
the file), so this backend is more thoroughly verified than the rest.

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
- **CSV file instead of Google Sheets, then Notion.** Each swap was at
  Nathan's request, each time to cut setup weight further: Sheets
  needed a Google Cloud service account (project, enabled API, IAM,
  downloaded key); Notion needed one integration token and sharing a
  database with it. A CSV file needs neither — it's just a file. Point
  `TRACKER_PATH` at a folder Google Drive for Desktop syncs to get it
  into Drive/your phone with no API involved at all. `src/lib/tracker.js`
  / `src/scripts/tracker_csv.py` were both exercised directly in this
  session, including cross-checking that a file written by one is read
  correctly by the other (fields containing commas, quotes, and literal
  newlines included) — real bugs in the first draft of the Node-side
  CSV parser were caught this way and fixed, not just assumed away.
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
    fetch-job-boards.py     Indeed (Selenium+cookie), RemoteOK/JustJoinIT/WWR (public APIs), LinkedIn (opt-in), Hacker News "Who is hiring?" (crawl4ai + Claude extraction, opt-in via --source hackernews)
    score-jobs.py            Claude API fit scoring -> CSV tracker
    tracker_csv.py           Python CSV read/append/update
    validate-config.js       Preflight credential/connectivity checks
  lib/
    config.js, logger.js, state.js, tracker.js   Node-side shared helpers
```

## Tracker fields (CSV)

`id | company | role | source | url | posted | salary | fitScore |
resumeUsed | formType | status | submittedDate | confirmationCode |
nextAction`

Status flows: `SCORED → FORM_FILLED → SUBMITTED` (or `REJECTED` /
`ERROR`).
