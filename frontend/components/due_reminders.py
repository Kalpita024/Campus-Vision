"""
due_reminders.py
-----------------
Reusable reminder banner component — meant to be imported and called
from inside other pages (e.g. Issued Books), not run as its own page.

Depends on:
  - services/library_api.py  -> get_due_reminders()
  - utils/styles.py          -> banner()
"""

import datetime
from services.library_api import get_due_reminders
from utils.styles import banner


def show_due_reminders(student_id: str, upcoming_window_days: int = 3) -> None:
    """
    Render overdue / due-soon / all-clear banners for the given student.
    Call this from inside any page, e.g.:

        from components.due_reminders import show_due_reminders
        show_due_reminders(student_id)
    """
    data = get_due_reminders(student_id, upcoming_window_days=upcoming_window_days)
    overdue_books = data["overdue"]
    upcoming_books = data["upcoming"]

    for b in overdue_books:
        days_late = datetime.date.today() - b["due_date"]
        banner(
            f"**{b['title']}** was due on {b['due_date'].strftime('%d %b %Y')} "
            f"— {days_late.days} day(s) overdue.",
            kind="overdue",
        )

    for b in upcoming_books:
        banner(
            f"**{b['title']}** is due on {b['due_date'].strftime('%d %b %Y')}. "
            f"Renew it from the Extend Date page if you need more time.",
            kind="upcoming",
        )

    if not overdue_books and not upcoming_books:
        banner("You're all caught up — no books overdue or due soon. 🎉", kind="ok")
