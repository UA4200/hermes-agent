#!/usr/bin/env python3
"""
ADAI INC — B2B Lead Sourcing Script
Discovers, enriches, qualifies, and outputs leads for dental/law/real-estate niches.

Usage:
  python source_leads.py discover --niche dental --city "Chicago, IL" --count 10
  python source_leads.py enrich --niche law --city "Chicago, IL" --count 5
  python source_leads.py pipeline --niche real-estate --city "Chicago, IL" --count 10 --output notion
  python source_leads.py export --niche dental --status qualified --format csv

Requires (set in ~/.hermes/.env or Alusi's secrets):
  TAVILY_API_KEY     - for tavily_search / tavily_extract
  APOLLO_API_KEY     - for Apollo contact/company search and enrichment
  HUNTER_API_KEY     - (optional) for email finding and verification
  NOTION_API_KEY     - for CRM storage
  NOTION_LEADS_DB_ID - ID of the Notion leads database
  AGENTMAIL_API_KEY  - for creating draft outreach
"""

import argparse
import csv
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
ENV_FILE = HERMES_HOME / ".env"


def _load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _get_key(name: str, required=True) -> str | None:
    val = os.environ.get(name)
    if not val and required:
        print(f"[ERROR] Missing {name} — add it to ~/.hermes/.env or Alusi's secrets.", file=sys.stderr)
        sys.exit(1)
    return val


def _http_get(url: str, headers: dict = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body[:300]}") from e


def _http_post(url: str, data: dict, headers: dict = None) -> dict:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        **(headers or {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body[:300]}") from e


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

ICP_QUERIES = {
    "dental": [
        '"{city}" independent dental practice owner -DSO -"dental group" -chain',
        '"{city}" dentist private practice contact email site:yelp.com OR site:healthgrades.com',
        '"{city}" dental office manager practice owner 4-15 employees',
    ],
    "law": [
        '"{city}" small law firm personal injury attorney 2-10 attorneys -"law group" -national',
        '"{city}" family law immigration attorney managing partner contact',
        '"{city}" attorney site:avvo.com OR site:findlaw.com 2 attorney office',
    ],
    "real-estate": [
        '"{city}" real estate team lead broker owner 5-20 agents',
        '"{city}" real estate agency owner contact email -Coldwell -Keller -RE/MAX',
        '"{city}" top real estate agent team leader site:zillow.com',
    ],
}

ZIPRECRUITER_SIGNALS = {
    "dental": ["dental front desk coordinator", "dental office manager", "patient care coordinator dental"],
    "law": ["law firm intake coordinator", "legal assistant intake", "legal office administrator"],
    "real-estate": ["real estate transaction coordinator", "real estate admin", "buyer agent coordinator"],
}


def discover_with_tavily(niche: str, city: str, count: int) -> list[dict]:
    """Use Tavily search API to discover prospect companies."""
    api_key = _get_key("TAVILY_API_KEY")
    leads = []
    queries = ICP_QUERIES.get(niche, [])

    for query_tmpl in queries:
        if len(leads) >= count:
            break
        query = query_tmpl.replace("{city}", city)
        try:
            result = _http_post(
                "https://api.tavily.com/search",
                {
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": 10,
                    "include_answer": False,
                },
            )
            for r in result.get("results", []):
                if len(leads) >= count:
                    break
                leads.append({
                    "source": "tavily",
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:300],
                    "niche": niche,
                    "city": city,
                    "status": "discovered",
                    "score": 0,
                })
        except Exception as e:
            print(f"[WARN] Tavily query failed: {e}", file=sys.stderr)

    return leads


def discover_growth_signals(niche: str, city: str) -> list[dict]:
    """Use ZipRecruiter to find companies actively hiring admin roles (growth signal)."""
    signals = ZIPRECRUITER_SIGNALS.get(niche, [])
    results = []
    # ZipRecruiter MCP is available as mcp__e48d58b6-*
    # This function returns query params for Alusi to execute via the MCP tool.
    # When running standalone, we just print the suggested queries.
    print(f"\n[GROWTH SIGNAL] Use ZipRecruiter MCP (mcp__e48d58b6__search_jobs) with:")
    for s in signals:
        print(f'  query="{s}", location="{city}", radius=25')
    print("  → Companies hiring these roles RIGHT NOW = feeling the admin pain = hot ICP\n")
    return results


# ---------------------------------------------------------------------------
# Enrichment
# ---------------------------------------------------------------------------

def enrich_with_apollo(company_name: str, domain: str = None) -> dict:
    """Enrich company via Apollo organizations endpoint."""
    api_key = _get_key("APOLLO_API_KEY")
    payload = {"api_key": api_key}
    if domain:
        payload["domain"] = domain
    else:
        payload["name"] = company_name
    try:
        result = _http_post(
            "https://api.apollo.io/v1/organizations/enrich",
            payload,
            headers={"Cache-Control": "no-cache"},
        )
        org = result.get("organization", {})
        return {
            "company_name": org.get("name", company_name),
            "domain": org.get("primary_domain", domain or ""),
            "employee_count": org.get("estimated_num_employees"),
            "city": org.get("city"),
            "state": org.get("state"),
            "phone": org.get("sanitized_phone"),
            "linkedin_url": org.get("linkedin_url"),
            "technologies": [t.get("name") for t in org.get("current_technologies", [])[:5]],
        }
    except Exception as e:
        print(f"[WARN] Apollo enrich failed for {company_name}: {e}", file=sys.stderr)
        return {"company_name": company_name, "domain": domain or ""}


def find_decision_maker(first_name: str, last_name: str, company_name: str, domain: str = None) -> dict:
    """Use Apollo people_match to find a specific person."""
    api_key = _get_key("APOLLO_API_KEY")
    payload = {
        "api_key": api_key,
        "first_name": first_name,
        "last_name": last_name,
        "organization_name": company_name,
    }
    if domain:
        payload["domain"] = domain
    try:
        result = _http_post(
            "https://api.apollo.io/v1/people/match",
            payload,
            headers={"Cache-Control": "no-cache"},
        )
        person = result.get("person") or {}
        return {
            "name": person.get("name", f"{first_name} {last_name}"),
            "title": person.get("title", ""),
            "email": person.get("email", ""),
            "phone": person.get("sanitized_phone", ""),
            "linkedin_url": person.get("linkedin_url", ""),
        }
    except Exception as e:
        print(f"[WARN] Apollo people_match failed: {e}", file=sys.stderr)
        return {}


def verify_email_hunter(first_name: str, last_name: str, domain: str) -> dict:
    """Find and verify email via Hunter.io API."""
    api_key = os.environ.get("HUNTER_API_KEY")
    if not api_key:
        print("[INFO] HUNTER_API_KEY not set — skipping email verification.", file=sys.stderr)
        return {}
    params = urllib.parse.urlencode({
        "domain": domain,
        "first_name": first_name,
        "last_name": last_name,
        "api_key": api_key,
    })
    try:
        result = _http_get(f"https://api.hunter.io/v2/email-finder?{params}")
        data = result.get("data", {})
        return {
            "email": data.get("email", ""),
            "confidence": data.get("score", 0),
            "verified": data.get("verification", {}).get("status") == "valid",
        }
    except Exception as e:
        print(f"[WARN] Hunter.io lookup failed: {e}", file=sys.stderr)
        return {}


# ---------------------------------------------------------------------------
# Lead Scoring
# ---------------------------------------------------------------------------

def score_lead(lead: dict) -> int:
    """Score a lead 0–8 based on ICP match signals."""
    score = 0
    niche = lead.get("niche", "")

    emp = lead.get("employee_count") or 0
    if niche == "dental" and 4 <= emp <= 15:
        score += 2
    elif niche == "law" and 2 <= emp <= 30:
        score += 2
    elif niche == "real-estate" and 3 <= emp <= 50:
        score += 2

    if lead.get("growth_signal"):
        score += 2

    technologies = [t.lower() for t in (lead.get("technologies") or [])]
    automation_tools = {"zapier", "make", "n8n", "hubspot", "salesforce", "activecampaign"}
    if not any(t in automation_tools for t in technologies):
        score += 1

    title = (lead.get("decision_maker_title") or "").lower()
    owner_signals = {"owner", "partner", "founder", "principal", "dr.", "doctor"}
    if any(s in title for s in owner_signals):
        score += 1

    is_independent = not any(
        s in (lead.get("company_name") or "").lower()
        for s in ["group", "associates llp", "keller", "coldwell", "re/max", "dso", "dental care"]
    )
    if is_independent:
        score += 1

    if lead.get("email"):
        score += 1

    return min(score, 8)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def push_to_notion(leads: list[dict]) -> None:
    """Create pages in the Notion leads database."""
    api_key = _get_key("NOTION_API_KEY")
    db_id = _get_key("NOTION_LEADS_DB_ID")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
    }

    for lead in leads:
        props = {
            "Name": {"title": [{"text": {"content": lead.get("decision_maker_name") or lead.get("title") or "Unknown"}}]},
            "Company": {"rich_text": [{"text": {"content": lead.get("company_name", "")}}]},
            "Niche": {"select": {"name": lead.get("niche", "").replace("-", " ").title()}},
            "Email": {"email": lead.get("email") or None},
            "Website": {"url": lead.get("url") or None},
            "Score": {"number": lead.get("score", 0)},
            "Status": {"select": {"name": "Discovered" if lead.get("score", 0) < 4 else "Qualified"}},
            "City": {"rich_text": [{"text": {"content": lead.get("city", "")}}]},
            "Notes": {"rich_text": [{"text": {"content": lead.get("snippet", "")[:200]}}]},
        }
        if lead.get("growth_signal"):
            props["Growth Signal"] = {"rich_text": [{"text": {"content": lead["growth_signal"]}}]}

        payload = {
            "parent": {"database_id": db_id},
            "properties": props,
        }
        try:
            _http_post("https://api.notion.com/v1/pages", payload, headers=headers)
            print(f"  [Notion] Added: {lead.get('company_name', 'Unknown')}", file=sys.stderr)
        except Exception as e:
            print(f"  [WARN] Notion push failed: {e}", file=sys.stderr)


def export_csv(leads: list[dict], path: str) -> None:
    if not leads:
        print("[INFO] No leads to export.", file=sys.stderr)
        return
    fields = ["company_name", "decision_maker_name", "decision_maker_title",
              "email", "phone", "url", "city", "niche", "score", "growth_signal", "notes"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(leads)
    print(f"[OK] Exported {len(leads)} leads to {path}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_discover(args) -> list[dict]:
    print(f"[DISCOVER] Niche={args.niche} City={args.city} Count={args.count}")
    discover_growth_signals(args.niche, args.city)

    leads = []
    if os.environ.get("TAVILY_API_KEY"):
        leads = discover_with_tavily(args.niche, args.city, args.count)
    else:
        print("[INFO] TAVILY_API_KEY not set — using WebSearch fallback.", file=sys.stderr)
        print(f"\n[ACTION REQUIRED] Run these WebSearch queries manually:")
        for q in ICP_QUERIES.get(args.niche, []):
            print(f'  • {q.replace("{city}", args.city)}')
        print()

    print(json.dumps(leads, indent=2))
    return leads


def cmd_enrich(args) -> list[dict]:
    """Enrich a batch of leads — reads JSON from stdin or a file."""
    if args.input:
        leads = json.loads(Path(args.input).read_text())
    else:
        leads = json.loads(sys.stdin.read())

    enriched = []
    for lead in leads[:args.count]:
        domain = urllib.parse.urlparse(lead.get("url", "")).netloc or ""
        company = lead.get("company_name") or lead.get("title", "Unknown")

        print(f"  Enriching: {company} ({domain})", file=sys.stderr)
        org_data = enrich_with_apollo(company, domain if domain else None)
        lead.update(org_data)
        lead["score"] = score_lead(lead)
        enriched.append(lead)

    print(json.dumps(enriched, indent=2))
    return enriched


def cmd_pipeline(args) -> None:
    """Full pipeline: discover → enrich → score → output."""
    print(f"\n=== ADAI INC Lead Pipeline ===")
    print(f"Niche: {args.niche} | City: {args.city} | Count: {args.count} | Output: {args.output}\n")

    leads = discover_with_tavily(args.niche, args.city, args.count) if os.environ.get("TAVILY_API_KEY") else []
    discover_growth_signals(args.niche, args.city)

    enriched = []
    for lead in leads:
        domain = urllib.parse.urlparse(lead.get("url", "")).netloc
        org_data = enrich_with_apollo(lead.get("company_name", lead["title"]), domain or None)
        lead.update(org_data)
        lead["score"] = score_lead(lead)
        enriched.append(lead)

    qualified = [l for l in enriched if l.get("score", 0) >= 4]
    cold = [l for l in enriched if l.get("score", 0) < 4]

    print(f"\n[RESULTS] {len(enriched)} total | {len(qualified)} qualified | {len(cold)} cold")
    for l in qualified:
        print(f"  ★ Score {l['score']}/8 — {l.get('company_name', 'Unknown')} ({l.get('city', '')})")

    if args.output == "notion":
        if os.environ.get("NOTION_API_KEY") and os.environ.get("NOTION_LEADS_DB_ID"):
            print("\n[NOTION] Pushing qualified leads...")
            push_to_notion(qualified)
        else:
            print("[WARN] NOTION_API_KEY or NOTION_LEADS_DB_ID not set — skipping Notion push.", file=sys.stderr)
    elif args.output == "csv":
        out_path = f"leads_{args.niche}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.csv"
        export_csv(qualified, out_path)
    else:
        print(json.dumps(qualified, indent=2))

    print(f"\n[NEXT STEPS]")
    print(f"  1. Review qualified leads above")
    print(f"  2. Source decision-maker names (LinkedIn / company website)")
    print(f"  3. Run: python source_leads.py enrich --niche {args.niche} --count {len(qualified)}")
    print(f"  4. Tell Nathan to approve AgentMail drafts with GO")
    print()

    if not os.environ.get("TAVILY_API_KEY"):
        print("[MISSING TOOL] Add TAVILY_API_KEY to unlock automated discovery.")
    if not os.environ.get("HUNTER_API_KEY"):
        print("[MISSING TOOL] Add HUNTER_API_KEY (hunter.io) for email verification.")
    if not os.environ.get("FIRECRAWL_API_KEY"):
        print("[MISSING TOOL] Add FIRECRAWL_API_KEY (firecrawl.dev) for directory scraping.")
    print()


def cmd_export(args) -> None:
    """Export leads from Notion to CSV for Instantly import."""
    api_key = _get_key("NOTION_API_KEY")
    db_id = _get_key("NOTION_LEADS_DB_ID")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
    }
    filter_payload = {
        "filter": {
            "and": [
                {"property": "Niche", "select": {"equals": args.niche.replace("-", " ").title()}},
                {"property": "Status", "select": {"equals": args.status.title()}},
            ]
        }
    }
    try:
        result = _http_post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            filter_payload,
            headers=headers,
        )
    except Exception as e:
        print(f"[ERROR] Notion query failed: {e}", file=sys.stderr)
        sys.exit(1)

    leads = []
    for page in result.get("results", []):
        props = page.get("properties", {})
        def _text(key):
            items = props.get(key, {}).get("rich_text", [])
            return items[0]["text"]["content"] if items else ""
        def _title(key):
            items = props.get(key, {}).get("title", [])
            return items[0]["text"]["content"] if items else ""
        leads.append({
            "company_name": _text("Company"),
            "decision_maker_name": _title("Name"),
            "email": props.get("Email", {}).get("email", ""),
            "niche": props.get("Niche", {}).get("select", {}).get("name", ""),
            "score": props.get("Score", {}).get("number", 0),
            "url": props.get("Website", {}).get("url", ""),
            "city": _text("City"),
            "notes": _text("Notes"),
        })

    if args.format == "csv":
        out_path = f"export_{args.niche}_{args.status}.csv"
        export_csv(leads, out_path)
    else:
        print(json.dumps(leads, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    _load_env()
    parser = argparse.ArgumentParser(description="ADAI INC B2B Lead Sourcing")
    sub = parser.add_subparsers(dest="command", required=True)

    p_discover = sub.add_parser("discover", help="Discover prospects via Tavily/WebSearch")
    p_discover.add_argument("--niche", choices=["dental", "law", "real-estate"], required=True)
    p_discover.add_argument("--city", required=True)
    p_discover.add_argument("--count", type=int, default=10)
    p_discover.set_defaults(func=cmd_discover)

    p_enrich = sub.add_parser("enrich", help="Enrich leads via Apollo + Hunter (reads JSON from stdin)")
    p_enrich.add_argument("--niche", choices=["dental", "law", "real-estate"])
    p_enrich.add_argument("--city")
    p_enrich.add_argument("--count", type=int, default=10)
    p_enrich.add_argument("--input", help="Input JSON file (default: stdin)")
    p_enrich.set_defaults(func=cmd_enrich)

    p_pipeline = sub.add_parser("pipeline", help="Full pipeline: discover → enrich → score → output")
    p_pipeline.add_argument("--niche", choices=["dental", "law", "real-estate"], required=True)
    p_pipeline.add_argument("--city", required=True)
    p_pipeline.add_argument("--count", type=int, default=10)
    p_pipeline.add_argument("--output", choices=["json", "csv", "notion"], default="json")
    p_pipeline.set_defaults(func=cmd_pipeline)

    p_export = sub.add_parser("export", help="Export leads from Notion to CSV for Instantly")
    p_export.add_argument("--niche", choices=["dental", "law", "real-estate"], required=True)
    p_export.add_argument("--status", default="qualified")
    p_export.add_argument("--format", choices=["json", "csv"], default="csv")
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
