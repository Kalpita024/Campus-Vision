"""
components/due_reminders.py
----------------------------
Reusable component that shows overdue + due-soon banners for a list of
already-fetched issued books. Call show_due_reminders(books) from any page
that already has the books list (e.g. 3_Issued_Books.py).

Depends on:
  - utils/styles.py -> section_title(), banner()
"""

import datetime

import streamlit as st
from utils.styles import section_title, banner


def show_due_reminders(books, reminder_window_days: int = 3):
    """
    Renders overdue and due-soon reminder banners for the given books.

    Args:
        books: list of book dicts, each needs 'title' and 'due_date'
               (a datetime.date)
        reminder_window_days: how many days ahead counts as "due soon"
    """
    today = datetime.date.today()

    overdue_books = [b for b in books if b["due_date"] < today]
    upcoming_books = [
        b for b in books
        if today <= b["due_date"] <= today + datetime.timedelta(days=reminder_window_days)
    ]

    section_title("Due Date Reminders")

    if overdue_books:
        st.subheader("⚠️ Overdue")
        for b in overdue_books:
            days_late = today - b["due_date"]
            banner(
                f"**{b['title']}** was due on {b['due_date'].strftime('%d %b %Y')} "
                f"— {days_late.days} day(s) overdue.",
                kind="overdue",
            )

    if upcoming_books:
        st.subheader("⏰ Due Soon")
        for b in upcoming_books:
            banner(
                f"**{b['title']}** is due on {b['due_date'].strftime('%d %b %Y')}. "
                f"Renew it from the Extend Date page if you need more time.",
                kind="upcoming",
            )

    if not overdue_books and not upcoming_books:
        banner("You're all caught up — no books overdue or due soon. 🎉", kind="ok")