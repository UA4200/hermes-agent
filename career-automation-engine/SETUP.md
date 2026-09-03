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
```

## 2. Credentials

```bash
cp .env.example .env
```

**Claude API key** — from console.anthropic.com.

**Google Sheets — service account (not a bare API key):**
1. console.cloud.google.com → new or existing project
2. Enable the "Google Sheets API"
3. IAM & Admin → Service Accounts → Create → Keys → Add key → JSON
4. Save the downloaded file as `service-account.json` in this folder
   (already gitignored)
5. Open the tracker sheet → Share → paste the service account's
   `...@...iam.gserviceaccount.com` email → give it Editor access
6. Set `GOOGLE_SHEET_ID` and `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` in `.env`

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

Fix anything marked `✗` before moving on — in particular the Sheets
connection check, which will fail if the service account hasn't been
shared onto the sheet (step 2.5 above) even if the key file is valid.

## 4. Discover + score

```bash
python3 src/scripts/fetch-job-boards.py --source indeed --limit 18
python3 src/scripts/score-jobs.py --input data/jobs_discovered.json
```

Check the tracker sheet: rows should appear with `status=SCORED` and a
`fitScore`. Add more boards with `--source remoteok`, `--source justjoinit`,
`--source weworkremotely`, each followed by its own `score-jobs.py --input ...`
call (or point `score-jobs.py` at a merged file).

## 5. Run the automation

```bash
bash start-automation.sh
```

Starts `dashboard-server.js` and `job-processor.js` as two background
processes, logging to `logs/dashboard.log` and `logs/processor.log`.
Open **http://localhost:3000**.

Stop with `bash stop-automation.sh`.

## Troubleshooting

- **"Google service account key not found"** — check `GOOGLE_SERVICE_ACCOUNT_KEY_PATH`
  points at the real file, relative to where you run the command from.
- **Sheets writes fail with a permissions error** — the service account
  email isn't shared onto the sheet as an Editor (step 2.5).
- **Playwright can't launch Chromium** — run `npx playwright install chromium`.
- **Dashboard shows "Dashboard server unreachable"** — `dashboard-server.js`
  isn't running; check `logs/dashboard.log`.
- **Dashboard stuck on "Idle" forever** — `job-processor.js` isn't
  running, or found zero jobs at/above `FIT_THRESHOLD`; check
  `logs/processor.log` and the tracker sheet's `fitScore` column.
- **Indeed/LinkedIn scraping returns nothing** — session cookie expired;
  get a fresh one (step 2).
