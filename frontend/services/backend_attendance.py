"""
services/backend_attendance.py
------------------------------
Sends attendance to the Flask backend (POST /api/attendance/mark-bulk) so it
appears in the Student Record page and the defaulters list.

Teachers only: the backend rejects any other login token.
"""

import requests

from services.auth_api import BACKEND_URL, TIMEOUT_SECONDS


def push_attendance(token: str, subject: str, on_date: str, records: dict):
    """
    records = {"UMIT2026045": "Present", "UMIT2026046": "Absent", ...}
    on_date = "YYYY-MM-DD"

    Returns (summary, error, offline):
      summary = {"saved": <int>, "not_found": [ids the backend doesn't know]}
      offline = True when the backend server is not running.
    """
    saved = 0
    not_found = []

    # The backend marks one status per call, so send Present and Absent separately.
    for status in ("Present", "Absent"):
        ids = [sid for sid, st_ in records.items() if st_ == status]
        if not ids:
            continue
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/attendance/mark-bulk",
                json={
                    "students": ids,
                    "subject": subject,
                    "date": on_date,
                    "status": status,
                    "method": "face",
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=TIMEOUT_SECONDS,
            )
        except requests.exceptions.RequestException:
            return None, "Cannot reach the backend server.", True

        if response.status_code == 401:
            return None, "Your login has expired. Please log out and log in again.", False
        if response.status_code == 403:
            return None, "Only teachers can mark attendance.", False

        try:
            body = response.json()
        except ValueError:
            return None, "The server sent an unexpected reply.", False

        if response.status_code != 200 or not body.get("success"):
            return None, body.get("message") or body.get("error") or "Save failed.", False

        data = body.get("data") or {}
        saved += len(data.get("marked", []))
        not_found += data.get("not_found", [])

    return {"saved": saved, "not_found": not_found}, None, False
