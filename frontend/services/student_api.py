"""
student_api.py
--------------
Calls the backend's roll-number lookup endpoint (teachers only).
"""

from urllib.parse import quote

import requests

from services.auth_api import BACKEND_URL, TIMEOUT_SECONDS


def get_record_by_roll_no(roll_no: str, token: str):
    """
    Look up one student's profile, library record and attendance record.

    Returns (record, error, offline):
      - found:            (dict, None, False)
      - not found / denied: (None, "message", False)
      - backend not up:   (None, "message", True)
    """
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/students/by-roll/{quote(roll_no.strip(), safe='')}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException:
        return None, "Cannot reach the backend server.", True

    try:
        data = response.json()
    except ValueError:
        return None, "The server sent an unexpected reply.", False

    if response.status_code == 200:
        return data, None, False

    if response.status_code == 401:
        return None, "Your login has expired. Please log out and log in again.", False

    if response.status_code == 403:
        return None, "Only teachers can look up student records.", False

    return None, data.get("error", "Lookup failed."), False