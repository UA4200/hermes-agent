"""Scores discovered jobs with the Claude API and writes qualifying rows
(fitScore >= FIT_THRESHOLD) to the Google Sheets tracker.

Usage:
    python score-jobs.py --source indeed --limit 18
    python score-jobs.py --input data/jobs_discovered.json
"""
import argparse
import importlib.util
import json
import os
import sys

import anthropic
from dotenv import load_dotenv

from sheets_client import SheetsClient

load_dotenv()

HERE = os.path.dirname(__file__)
DATA_PATH = os.path.join(HERE, "..", "..", "data", "jobs_discovered.json")

RUBRIC = """You are scoring job postings for Nathan Asiegbu, a PMP-certified \
technology and AI program manager (10+ years) across healthcare IT, \
emergency management, clinical research, data management, security/compliance, \
enterprise technology, AI strategy, and ERP/workforce-management programs. \
Toolkit: Python, APIs, SQL, n8n, AWS, Azure, Power BI, Tableau, Jira, \
Confluence, ServiceNow, automation, governance, KPI-driven program management.

For each job below, return a 0-100 fit score and one-sentence reasoning, based on:
- Title match (Senior TPM, AI PM, Healthcare IT PM, etc.)
- Requirements match (skills, years of experience, certifications)
- Keyword match (Epic, EHR, cloud, data, compliance, healthcare, AI/ML programs)

Return ONLY a JSON array, one object per job in the same order given, each:
{"score": <0-100 int>, "reasoning": "<one sentence>"}

Jobs:
"""


def load_fetchers():
    spec = importlib.util.spec_from_file_location(
        "fetch_job_boards", os.path.join(HERE, "fetch-job-boards.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_jobs(args, existing_urls):
    if args.input:
        with open(args.input) as f:
            jobs = json.load(f)
    elif args.source:
        fetchers = load_fetchers()
        if args.source == "indeed":
            jobs = fetchers.fetch_indeed_saved(limit=args.limit)
        elif args.source == "remoteok":
            jobs = fetchers.fetch_remoteok()
        elif args.source == "justjoinit":
            jobs = fetchers.fetch_justjoinit()
        elif args.source == "weworkremotely":
            jobs = fetchers.fetch_weworkremotely()
        else:
            print(f"Unknown --source {args.source}. Run fetch-job-boards.py first and use --input instead.", file=sys.stderr)
            sys.exit(1)
    elif os.path.exists(DATA_PATH):
        with open(DATA_PATH) as f:
            jobs = json.load(f)
    else:
        print("Nothing to score — pass --source or --input, or run fetch-job-boards.py first.", file=sys.stderr)
        sys.exit(1)

    return [j for j in jobs if j.get("url") not in existing_urls]


def score_batch(client, model, batch):
    listing = "\n\n".join(
        f"{i+1}. {j['title']} at {j['company']}\n{j.get('description', '')[:800]}"
        for i, j in enumerate(batch)
    )
    resp = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": RUBRIC + listing}],
    )
    text = resp.content[0].text.strip()
    # Claude sometimes wraps JSON in a code fence — strip it defensively.
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="indeed | remoteok | justjoinit | weworkremotely")
    parser.add_argument("--input", help="Path to a jobs_discovered.json-shaped file")
    parser.add_argument("--limit", type=int, default=18)
    args = parser.parse_args()

    claude_key = os.environ.get("CLAUDE_API_KEY")
    if not claude_key:
        print("CLAUDE_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)
    model = os.environ.get("CLAUDE_MODEL", "claude-opus-5")
    batch_size = int(os.environ.get("CLAUDE_BATCH_SIZE", "10"))
    threshold = int(os.environ.get("FIT_THRESHOLD", "70"))

    sheets = SheetsClient(
        sheet_id=os.environ["GOOGLE_SHEET_ID"],
        key_path=os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY_PATH", "./service-account.json"),
    )
    existing_urls = sheets.existing_urls()

    jobs = load_jobs(args, existing_urls)
    if not jobs:
        print("No new jobs to score (already in tracker, or none found).")
        return

    client = anthropic.Anthropic(api_key=claude_key)
    scored_rows = []
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        try:
            results = score_batch(client, model, batch)
        except Exception as e:
            print(f"Scoring batch {i // batch_size + 1} failed: {e}", file=sys.stderr)
            continue
        for job, result in zip(batch, results):
            score = int(result.get("score", 0))
            if score < threshold:
                continue
            scored_rows.append({
                "company": job.get("company", ""),
                "role": job.get("title", ""),
                "source": job.get("source", ""),
                "url": job.get("url", ""),
                "posted": job.get("posted", ""),
                "salary": job.get("salary") or "",
                "fitScore": score,
                "resumeUsed": "",
                "formType": "",
                "status": "SCORED",
                "nextAction": result.get("reasoning", ""),
            })

    if not scored_rows:
        print(f"No jobs scored {threshold}+ out of {len(jobs)} evaluated.")
        return

    sheets.append_jobs(scored_rows)
    print(f"Wrote {len(scored_rows)} jobs scoring {threshold}+ to the tracker (out of {len(jobs)} evaluated).")


if __name__ == "__main__":
    main()
