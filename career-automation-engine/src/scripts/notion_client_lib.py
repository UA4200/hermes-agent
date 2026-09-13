"""Notion database tracker access for the Python side (score-jobs.py).

Mirrors src/lib/notion.js — same field set, same REST API, same
2025-09-03 data-source model (queries/creates go against a data SOURCE
id, not the database id).

Named notion_client_lib rather than notion_client to avoid shadowing the
real `notion-client` PyPI package if it's ever installed alongside this.
"""
import requests

API = "https://api.notion.com/v1"
VERSION = "2025-09-03"

PROP = {
    "company": "Company", "role": "Role", "source": "Source", "url": "URL",
    "posted": "Posted", "salary": "Salary", "fitScore": "Fit Score",
    "resumeUsed": "Resume Used", "formType": "Form Type", "status": "Status",
    "submittedDate": "Submitted Date", "confirmationCode": "Confirmation",
    "nextAction": "Next Action",
}
TITLE_FIELD = "company"
SELECT_FIELDS = {"source", "formType", "status"}
URL_FIELDS = {"url"}
NUMBER_FIELDS = {"fitScore"}


def _to_property_value(field, value):
    if field == TITLE_FIELD:
        return {"title": [{"text": {"content": str(value or "")[:2000]}}]}
    if field in SELECT_FIELDS:
        return {"select": {"name": str(value)[:100]}} if value else {"select": None}
    if field in URL_FIELDS:
        return {"url": value or None}
    if field in NUMBER_FIELDS:
        return {"number": None if value in (None, "") else float(value)}
    return {"rich_text": [{"text": {"content": str(value or "")[:2000]}}]}


def _from_page(page):
    props = page["properties"]

    def get(field):
        p = props.get(PROP[field])
        if not p:
            return ""
        t = p["type"]
        if t == "title":
            return "".join(x["plain_text"] for x in p["title"])
        if t == "rich_text":
            return "".join(x["plain_text"] for x in p["rich_text"])
        if t == "select":
            return p["select"]["name"] if p["select"] else ""
        if t == "url":
            return p["url"] or ""
        if t == "number":
            return p["number"] if p["number"] is not None else ""
        return ""

    job = {"pageId": page["id"]}
    for field in PROP:
        job[field] = get(field)
    return job


class NotionClient:
    def __init__(self, api_key: str, data_source_id: str):
        if not api_key:
            raise ValueError("NOTION_API_KEY not set — see SETUP.md.")
        self.data_source_id = data_source_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": VERSION,
            "Content-Type": "application/json",
        }

    def _request(self, method, path, **kwargs):
        resp = requests.request(method, f"{API}{path}", headers=self.headers, timeout=20, **kwargs)
        if not resp.ok:
            raise RuntimeError(f"Notion API {path} failed: {resp.status_code} {resp.text}")
        return resp.json()

    def read_all_jobs(self):
        jobs = []
        cursor = None
        while True:
            body = {"start_cursor": cursor} if cursor else {}
            data = self._request("POST", f"/data_sources/{self.data_source_id}/query", json=body)
            jobs.extend(_from_page(p) for p in data["results"])
            if not data.get("has_more"):
                break
            cursor = data["next_cursor"]
        return jobs

    def existing_urls(self):
        return {j["url"] for j in self.read_all_jobs() if j.get("url")}

    def append_jobs(self, jobs: list[dict]):
        for job in jobs:
            full = {"status": "SCORED", **job}
            properties = {
                PROP[field]: _to_property_value(field, full[field])
                for field in PROP if field in full
            }
            self._request("POST", "/pages", json={
                "parent": {"type": "data_source_id", "data_source_id": self.data_source_id},
                "properties": properties,
            })

    def update_row(self, page_id: str, fields: dict):
        properties = {PROP[k]: _to_property_value(k, v) for k, v in fields.items()}
        self._request("PATCH", f"/pages/{page_id}", json={"properties": properties})
