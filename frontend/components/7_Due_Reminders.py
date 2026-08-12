"""
7_Due_Reminders.py
-------------------
Shows the student a clear banner list of:
  - Overdue books (red)
  - Books due soon (yellow, within the reminder window)
  - A green "all clear" message if nothing is due

Depends on:
  - services/library_api.py  -> get_due_reminders()
  - utils/styles.py          -> load_custom_css(), banner(), section_title()
"""

import os
import sys

# --- Make sure Python can find the frontend/services and frontend/utils
# packages when Streamlit runs this file directly as a page. ---
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if FRONTEND_DIR not in sys.path:
    sys.path.append(FRONTEND_DIR)

import datetime

import streamlit as st
from services.library_api import get_due_reminders
from utils.styles import load_custom_css, section_title, banner

# ---------------------------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Due Reminders", page_icon="📚")
load_custom_css()

# TODO: replace with the real logged-in student's ID once auth/session
# state is wired up (check what app.py stores in st.session_state).
student_id = st.session_state.get("student_id", "demo_student")

section_title("Due Date Reminders")

reminder_window = st.slider(
    "Show books due within (days)", min_value=1, max_value=14, value=3
)

data = get_due_reminders(student_id, upcoming_window_days=reminder_window)
overdue_books = data["overdue"]
upcoming_books = data["upcoming"]

# ---------------------------------------------------------------------------
# OVERDUE SECTION
# ---------------------------------------------------------------------------

if overdue_books:
    st.subheader("⚠️ Overdue")
    for b in overdue_books:
        days_late = datetime.date.today() - b["due_date"]
        banner(
            f"**{b['title']}** was due on {b['due_date'].strftime('%d %b %Y')} "
            f"— {days_late.days} day(s) overdue.",
            kind="overdue",
        )

# ---------------------------------------------------------------------------
# UPCOMING SECTION
# ---------------------------------------------------------------------------

if upcoming_books:
    st.subheader("⏰ Due Soon")
    for b in upcoming_books:
        banner(
            f"**{b['title']}** is due on {b['due_date'].strftime('%d %b %Y')}. "
            f"Renew it from the Extend Date page if you need more time.",
            kind="upcoming",
        )

# ---------------------------------------------------------------------------
# ALL CLEAR
# ---------------------------------------------------------------------------

if not overdue_books and not upcoming_books:
    banner("You're all caught up — no books overdue or due soon. 🎉", kind="ok")

st.divider()
st.caption(
    "Reminders are based on issued-book due dates. "
    "This page currently reads from stub data in `library_api.py`; "
    "it will automatically show real data once the backend is connected."
)
