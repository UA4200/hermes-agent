"""Google Sheets tracker access for the Python side (scoring + discovery).

Mirrors src/lib/sheets.js — same 13-column schema, same service-account
auth (a bare API key can't write rows). Kept intentionally small: this
project needs read-all / append / update-by-row, nothing more.
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

COLUMNS = [
    "company", "role", "source", "url", "posted", "salary",
    "fitScore", "resumeUsed", "formType", "status",
    "submittedDate", "confirmationCode", "nextAction",
]
SHEET_RANGE = "Sheet1!A:M"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsClient:
    def __init__(self, sheet_id: str, key_path: str):
        if not os.path.exists(key_path):
            raise FileNotFoundError(
                f"Google service account key not found at {key_path}. See SETUP.md step 2."
            )
        creds = service_account.Credentials.from_service_account_file(key_path, scopes=SCOPES)
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet_id = sheet_id

    def read_all_jobs(self):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range=SHEET_RANGE
        ).execute()
        rows = result.get("values", [])[1:]  # skip header
        jobs = []
        for i, row in enumerate(rows):
            job = {col: (row[idx] if idx < len(row) else "") for idx, col in enumerate(COLUMNS)}
            job["rowNumber"] = i + 2
            jobs.append(job)
        return jobs

    def existing_urls(self):
        return {j["url"] for j in self.read_all_jobs() if j.get("url")}

    def append_jobs(self, jobs: list[dict]):
        values = [[job.get(col, "") for col in COLUMNS] for job in jobs]
        self.service.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range=SHEET_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": values},
        ).execute()

    def update_row(self, row_number: int, fields: dict):
        data = []
        for key, value in fields.items():
            col_index = COLUMNS.index(key)
            col_letter = chr(ord("A") + col_index)
            data.append({"range": f"Sheet1!{col_letter}{row_number}", "values": [[value]]})
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.sheet_id,
            body={"valueInputOption": "USER_ENTERED", "data": data},
        ).execute()
