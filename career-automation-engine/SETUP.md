# Setup

Run all of this on your own machine — not in a cloud Claude Code
session. The dashboard binds to `localhost`, and the browser Playwright
drives needs to actually be visible to you.

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- `npx playwright install chromium` (downloads the browser Playwright drives)

## 1. Install dependencies

```bash
cd career-automation-engine
npm install
pip install -r requirements.txt
npx playwright install chromium
crawl4ai-setup
```

`crawl4ai-setup` downloads crawl4ai's own browser (separate from the
Node Playwright install above) — only needed if you'll use
`fetch-job-boards.py --source hackernews`. `crawl4ai-doctor` diagnoses
setup issues if the source fails.

## 2. Credentials

```bash
cp .env.example .env
```

**Claude API key** — from console.anthropic.com.

**Tracker (optional: Google Drive)** — the default `TRACKER_PATH` in
`.env.example` (`./data/tracker.csv`) needs nothing — it just works.
To get the tracker into real Google Drive and your phone with zero API
setup:
1. Install [Google Drive for Desktop](https://www.google.com/drive/download/) if you don't have it, and let it finish syncing
2. Create a folder inside your synced Drive, e.g. "Career Application Engine"
3. Set `TRACKER_PATH` in `.env` to a file inside that folder, e.g.
   `~/Library/CloudStorage/GoogleDrive-you@gmail.com/My Drive/Career Application Engine/tracker.csv` (macOS)
   or `G:\My Drive\Career Application Engine\tracker.csv` (Windows)

Drive syncs the file automatically from there — no code involved.

**Indeed session cookie** (needed for `fetch-job-boards.py --source indeed`):
1. Sign into Indeed.com in Chrome
2. DevTools (F12) → Application → Cookies → indeed.com
3. Copy the `JSESSIONID` value into `INDEED_SESSION_COOKIE` in `.env`
4. This cookie expires (usually ~30 days) — repeat when scraping starts failing

Read the ToS-risk note in `README.md` before doing this — it applies
here and to `LINKEDIN_SESSION_COOKIE` if you choose to set that too.

**Resume + phone** — set `RESUME_PATH` (a real PDF on disk) and
`APPLICANT_PHONE` in `.env`.

## 3. Validate

```bash
node src/scripts/validate-config.js
```

Fix anything marked `✗` before moving on — the tracker check will fail
if `TRACKER_PATH`'s parent folder doesn't exist (e.g. a typo'd Drive
path) or isn't writable.

## 4. Discover + score

```bash
python3 src/scripts/fetch-job-boards.py --source indeed --limit 18
python3 src/scripts/score-jobs.py --input data/jobs_discovered.json
```

Check the tracker file (open `TRACKER_PATH` in Excel/Numbers/Sheets, or
just `cat` it): rows should appear with `status=SCORED` and a
`fitScore`. Add more boards with `--source remoteok`, `--source justjoinit`,
`--source weworkremotely`, each followed by its own `score-jobs.py --input ...`
call (or point `score-jobs.py` at a merged file). `--source hackernews`
pulls the current "Who is hiring?" thread (needs `crawl4ai-setup` above
and `CLAUDE_API_KEY`, since it uses Claude to pull structured postings
out of free-text comments) — not part of `--source all` since it's
slower and makes several Claude API calls per run.

## 5. Run the automation

```bash
bash start-automation.sh
```

Starts `dashboard-server.js` and `job-processor.js` as two background
processes, logging to `logs/dashboard.log` and `logs/processor.log`.
Open **http://localhost:3000**.

Stop with `bash stop-automation.sh`.

## Troubleshooting

- **Tracker writes fail with "ENOENT" or a permissions error** — the
  folder in `TRACKER_PATH` doesn't exist yet or isn't writable; create
  it (Drive Desktop needs the parent folder to already exist and be
  syncing) or fix the path.
- **Playwright can't launch Chromium** — run `npx playwright install chromium`.
- **Dashboard shows "Dashboard server unreachable"** — `dashboard-server.js`
  isn't running; check `logs/dashboard.log`.
- **Dashboard stuck on "Idle" forever** — `job-processor.js` isn't
  running, or found zero jobs at/above `FIT_THRESHOLD`; check
  `logs/processor.log` and the tracker file's `fitScore` column.
- **Indeed/LinkedIn scraping returns nothing** — session cookie expired;
  get a fresh one (step 2).
- **`hackernews` source fails to launch a browser** — run `crawl4ai-setup`
  (or `crawl4ai-doctor` to diagnose); it needs its own downloaded browser,
  separate from the Node Playwright install in step 1.
