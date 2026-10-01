"""
components/due_reminders.py
----------------------------
Reusable component that shows a student's due-book reminders
(overdue + due-soon banners). Import and call show_due_reminders()
from any page (e.g. Issued_Books, Dashboard) to display it inline.

Depends on:
  - services/library_api.py  -> get_due_reminders()
  - utils/styles.py          -> banner(), section_title()
"""

import datetime

import streamlit as st
from services.library_api import get_due_reminders
from utils.styles import section_title, banner


def show_due_reminders(student_id: str, reminder_window_days: int = 3):
    """
    Renders overdue and due-soon book reminders for the given student.

    Args:
        student_id: the logged-in student's ID
        reminder_window_days: how many days ahead counts as "due soon"
    """
    section_title("Due Date Reminders")

    data = get_due_reminders(student_id, upcoming_window_days=reminder_window_days)
    overdue_books = data["overdue"]
    upcoming_books = data["upcoming"]

    # ---------------- OVERDUE ----------------
    if overdue_books:
        st.subheader("⚠️ Overdue")
        for b in overdue_books:
            days_late = datetime.date.today() - b["due_date"]
            banner(
                f"**{b['title']}** was due on {b['due_date'].strftime('%d %b %Y')} "
                f"— {days_late.days} day(s) overdue.",
                kind="overdue",
            )

    # ---------------- DUE SOON ----------------
    if upcoming_books:
        st.subheader("⏰ Due Soon")
        for b in upcoming_books:
            banner(
                f"**{b['title']}** is due on {b['due_date'].strftime('%d %b %Y')}. "
                f"Renew it from the Extend Date page if you need more time.",
                kind="upcoming",
            )

    # ---------------- ALL CLEAR ----------------
    if not overdue_books and not upcoming_books:
        banner("You're all caught up — no books overdue or due soon. 🎉", kind="ok")
