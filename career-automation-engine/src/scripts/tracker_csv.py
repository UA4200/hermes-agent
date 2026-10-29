"""CSV tracker access for the Python side (score-jobs.py).

Mirrors src/lib/tracker.js — same field set, same file, same
read-whole-file/rewrite-whole-file approach (fine for single-user,
human-paced writes).
"""
import csv
import os
import random
import time

FIELDS = [
    "id", "company", "role", "source", "url", "posted", "salary",
    "fitScore", "resumeUsed", "formType", "status",
    "submittedDate", "confirmationCode", "nextAction",
]


class TrackerClient:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=FIELDS).writeheader()

    def read_all_jobs(self):
        with open(self.path, newline="") as f:
            return list(csv.DictReader(f))

    def existing_urls(self):
        return {j["url"] for j in self.read_all_jobs() if j.get("url")}

    def append_jobs(self, jobs: list[dict]):
        rows = self.read_all_jobs()
        for job in jobs:
            row_id = f"{int(time.time() * 1000)}{random.randint(1000, 9999)}"
            rows.append({"id": row_id, "status": "SCORED", **job})
        self._write(rows)

    def update_row(self, row_id: str, fields: dict):
        rows = self.read_all_jobs()
        for row in rows:
            if row["id"] == row_id:
                row.update(fields)
                self._write(rows)
                return
        raise ValueError(f"No tracker row with id {row_id}")

    def _write(self, rows):
        with open(self.path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in FIELDS})
