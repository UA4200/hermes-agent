"""Multi-source job discovery.

RemoteOK / JustJoinIT / We Work Remotely are public JSON APIs — no auth,
no ToS conflict, safe to run anywhere.

Indeed and LinkedIn require scraping a logged-in session (via your own
browser's session cookie) and run through Selenium. Both platforms'
Terms of Service restrict automated/bot access, and LinkedIn in
particular actively detects and bans automation — that's a real risk to
the account whose cookie you use, independent of anything this script
does carefully. Run these only with an account you're OK putting at
risk, only from your own machine, and keep concurrency/frequency low.
LinkedIn fetching is off unless you pass --include-linkedin explicitly.

Output: data/jobs_discovered.json, ready for score-jobs.py.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

TITLE_FILTER = re.compile(
    r"program manager|project manager|technical program|product manager|"
    r"\bAI\b|healthcare|health it|EHR|EPIC|clinical",
    re.IGNORECASE,
)

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "jobs_discovered.json")


def normalize(company, title, url, source, posted=None, location=None, salary=None, description=""):
    return {
        "company": company or "",
        "title": title or "",
        "url": url or "",
        "source": source,
        "posted": posted or datetime.now(timezone.utc).isoformat(),
        "location": location or "",
        "salary": salary,
        "description": description or "",
        "lastScraped": datetime.now(timezone.utc).isoformat(),
    }


def fetch_remoteok():
    try:
        resp = requests.get("https://remoteok.com/api", headers={"User-Agent": "career-automation-engine"}, timeout=15)
        resp.raise_for_status()
        jobs = resp.json()
    except Exception as e:
        print(f"[remoteok] fetch failed: {e}", file=sys.stderr)
        return []
    out = []
    for j in jobs:
        if not isinstance(j, dict) or "position" not in j:
            continue
        if not TITLE_FILTER.search(j.get("position", "")):
            continue
        out.append(normalize(
            company=j.get("company"), title=j.get("position"),
            url=j.get("url"), source="remoteok",
            posted=j.get("date"), location="Remote",
            salary=j.get("salary_min") and f"{j.get('salary_min')}-{j.get('salary_max')}",
            description=j.get("description", ""),
        ))
    print(f"[remoteok] {len(out)} matching jobs")
    return out


def fetch_justjoinit():
    try:
        resp = requests.get(
            "https://api.justjoinit.eu/v2/postings",
            params={"category_id": 3, "location_slug": "us"},
            timeout=15,
        )
        resp.raise_for_status()
        jobs = resp.json()
    except Exception as e:
        print(f"[justjoinit] fetch failed: {e}", file=sys.stderr)
        return []
    out = [
        normalize(
            company=j.get("company_name"), title=j.get("title"), url=j.get("url"),
            source="justjoinit", posted=j.get("published_at"),
            location=j.get("work_type"),
            salary=f"{j.get('salary_from')}-{j.get('salary_to')}" if j.get("salary_from") else None,
        )
        for j in jobs if isinstance(j, dict)
    ]
    print(f"[justjoinit] {len(out)} jobs")
    return out


def fetch_weworkremotely():
    try:
        resp = requests.get("https://weworkremotely.com/api/v3/posts", timeout=15)
        resp.raise_for_status()
        posts = resp.json().get("posts", [])
    except Exception as e:
        print(f"[weworkremotely] fetch failed: {e}", file=sys.stderr)
        return []
    out = []
    for p in posts:
        category = p.get("category", "") or ""
        if not re.search(r"management|program|pm", category, re.IGNORECASE):
            continue
        out.append(normalize(
            company=p.get("company_name"), title=p.get("title"),
            url=f"https://weworkremotely.com/remote-jobs/{p.get('permalink')}",
            source="weworkremotely", posted=p.get("created_at"), location="Remote",
        ))
    print(f"[weworkremotely] {len(out)} jobs")
    return out


def fetch_indeed_saved(limit=18):
    """Requires INDEED_SESSION_COOKIE in .env and a local Chrome/Chromium.
    Not run in headless cloud sessions — needs a real logged-in cookie
    lifted from your own browser (see SETUP.md)."""
    cookie = os.environ.get("INDEED_SESSION_COOKIE")
    if not cookie:
        print("[indeed] INDEED_SESSION_COOKIE not set — skipping.", file=sys.stderr)
        return []
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    out = []
    try:
        driver.get("https://www.indeed.com")
        driver.add_cookie({"name": "JSESSIONID", "value": cookie, "domain": ".indeed.com"})
        driver.get("https://www.indeed.com/resumes/my-applications")
        time.sleep(3)
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-jk]")[:limit]
        for c in cards:
            try:
                title = c.find_element(By.CSS_SELECTOR, "h2, .jobTitle").text
                company = c.find_element(By.CSS_SELECTOR, ".companyName").text
                job_key = c.get_attribute("data-jk")
                url = f"https://www.indeed.com/viewjob?jk={job_key}"
                out.append(normalize(company=company, title=title, url=url, source="indeed"))
            except Exception:
                continue
    except Exception as e:
        print(f"[indeed] scrape failed: {e}", file=sys.stderr)
    finally:
        driver.quit()
    print(f"[indeed] {len(out)} saved jobs")
    return out


def fetch_linkedin(query="Senior Program Manager", location="United States"):
    cookie = os.environ.get("LINKEDIN_SESSION_COOKIE")
    if not cookie:
        print("[linkedin] LINKEDIN_SESSION_COOKIE not set — skipping.", file=sys.stderr)
        return []
    print(
        "[linkedin] WARNING: automated LinkedIn access risks the account "
        "tied to this cookie being flagged or banned. Proceeding because "
        "--include-linkedin was passed.",
        file=sys.stderr,
    )
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from urllib.parse import quote

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    out = []
    try:
        driver.get("https://www.linkedin.com")
        driver.add_cookie({"name": "li_at", "value": cookie, "domain": ".linkedin.com"})
        url = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}&location={quote(location)}"
        driver.get(url)
        time.sleep(4)
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-job-id]")
        for c in cards:
            try:
                job_id = c.get_attribute("data-job-id")
                title = c.find_element(By.CSS_SELECTOR, "h3").text
                company = c.find_element(By.CSS_SELECTOR, "h4").text
                out.append(normalize(
                    company=company, title=title,
                    url=f"https://www.linkedin.com/jobs/view/{job_id}", source="linkedin",
                ))
            except Exception:
                continue
    except Exception as e:
        print(f"[linkedin] scrape failed: {e}", file=sys.stderr)
    finally:
        driver.quit()
    print(f"[linkedin] {len(out)} jobs")
    return out


def dedupe(jobs):
    seen = set()
    out = []
    for j in jobs:
        key = (j["company"].strip().lower(), j["title"].strip().lower(), j.get("location", "").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="all", help="all | indeed | remoteok | linkedin | justjoinit | weworkremotely")
    parser.add_argument("--limit", type=int, default=18)
    parser.add_argument("--include-linkedin", action="store_true", help="Explicitly opt in to LinkedIn scraping (account-risk, off by default)")
    args = parser.parse_args()

    jobs = []
    if args.source in ("all", "indeed"):
        jobs += fetch_indeed_saved(limit=args.limit)
    if args.source in ("all", "remoteok"):
        jobs += fetch_remoteok()
    if args.source in ("all", "justjoinit"):
        jobs += fetch_justjoinit()
    if args.source in ("all", "weworkremotely"):
        jobs += fetch_weworkremotely()
    if args.source == "linkedin" or (args.source == "all" and args.include_linkedin):
        jobs += fetch_linkedin()

    jobs = dedupe(jobs)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(jobs, f, indent=2)
    print(f"\nWrote {len(jobs)} deduplicated jobs to {OUT_PATH}")


if __name__ == "__main__":
    main()
