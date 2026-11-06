"""
auth_api.py
-----------
Calls the Flask backend's login endpoint.

BACKEND_URL can be overridden with an environment variable when the
backend is hosted somewhere other than your own laptop.
"""

import os

import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
TIMEOUT_SECONDS = 5


def login(role: str, user_id: str, password: str = ""):
    """
    Try to log in through the backend.

    Returns (result, error, offline):
      - success:          (dict with token/name/user_id/role, None, False)
      - wrong details:    (None, "message from the server", False)
      - backend not up:   (None, "message", True)
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"role": role, "user_id": user_id, "password": password},
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

    return None, data.get("error", "Login failed."), False