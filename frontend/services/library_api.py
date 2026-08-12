"""
library_api.py
--------------
Stub functions that simulate backend calls for the Library module.

Right now everything runs on an in-memory dummy dataset so the rest of the
team can build UI pages before the Flask backend + database are ready.

WHEN THE BACKEND IS READY:
Replace the body of each function with a real HTTP call, e.g.

    import requests
    def get_issued_books(student_id):
        resp = requests.get(f"{BASE_URL}/api/library/issued/{student_id}")
        resp.raise_for_status()
        return resp.json()

Keep the function names and return shapes the SAME so no other file
(due_reminders.py, extend_date.py, issued_books.py, library_card.py) has
to change when you swap dummy data for real data.
"""

import datetime
from typing import Dict, List

# ---------------------------------------------------------------------------
# CONFIG (used later when wiring up the real backend)
# ---------------------------------------------------------------------------

BASE_URL = "http://localhost:5000"  # TODO: update once backend teammate shares the URL

# ---------------------------------------------------------------------------
# DUMMY "DATABASE"
# In-memory list acting as a stand-in for the issued_book collection/table.
# Streamlit re-runs the script on every interaction, so this resets each
# session — that's expected for now. Session-state usage happens in the
# page files (e.g. extend_date.py), not here.
# ---------------------------------------------------------------------------

_DUMMY_ISSUED_BOOKS: List[Dict] = [
    {
        "book_id": "B001",
        "title": "Introduction to Algorithms",
        "author": "Cormen, Leiserson, Rivest, Stein",
        "issue_date": datetime.date(2026, 7, 22),
        "due_date": datetime.date(2026, 8, 9),   # overdue relative to "today" for demo
        "renewed": False,
        "returned": False,
    },
    {
        "book_id": "B002",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "issue_date": datetime.date(2026, 8, 1),
        "due_date": datetime.date(2026, 8, 13),  # due soon
        "renewed": False,
        "returned": False,
    },
    {
        "book_id": "B003",
        "title": "Deep Learning",
        "author": "Ian Goodfellow",
        "issue_date": datetime.date(2026, 7, 15),
        "due_date": datetime.date(2026, 8, 25),  # comfortably not due yet
        "renewed": False,
        "returned": False,
    },
]

# ---------------------------------------------------------------------------
# DUMMY STUDENT PROFILE
# Stand-in for a students collection/table until the backend is ready.
# ---------------------------------------------------------------------------

_DUMMY_STUDENT_PROFILE: Dict = {
    "student_id": "UMIT2026045",
    "name": "Kalpita Naik",
    "department": "AI & Data Science",
    "valid_till": datetime.date(2027, 6, 30),
}


# ---------------------------------------------------------------------------
# PUBLIC STUB FUNCTIONS
# ---------------------------------------------------------------------------

def get_student_profile(student_id: str) -> Dict:
    """
    Return basic profile info for the digital library card.

    TODO(backend): GET /api/students/<student_id>
    """
    profile = dict(_DUMMY_STUDENT_PROFILE)
    profile["student_id"] = student_id  # reflect whichever ID was passed in
    return profile


def get_issued_books(student_id: str) -> List[Dict]:
    """
    Return all currently-issued (not yet returned) books for a student.

    TODO(backend): GET /api/library/issued/<student_id>
    """
    # student_id is unused for now since the dummy data isn't per-student;
    # keep the parameter so the real API call already has the right signature.
    return [b for b in _DUMMY_ISSUED_BOOKS if not b["returned"]]


def get_due_reminders(student_id: str, upcoming_window_days: int = 3) -> Dict[str, List[Dict]]:
    """
    Split issued books into 'overdue' and 'upcoming' (due within
    `upcoming_window_days` days). Used by due_reminders.py to build banners.

    TODO(backend): could become GET /api/library/reminders/<student_id>
    or stay client-side if the backend just returns issued_books with dates.
    """
    today = datetime.date.today()
    books = get_issued_books(student_id)

    overdue = [b for b in books if b["due_date"] < today]
    upcoming = [
        b for b in books
        if today <= b["due_date"] <= today + datetime.timedelta(days=upcoming_window_days)
    ]
    return {"overdue": overdue, "upcoming": upcoming}


def extend_due_date(book_id: str, extra_days: int = 7) -> Dict:
    """
    Extend (renew) a book's due date by `extra_days`, once only.

    Returns: {"success": bool, "message": str, "new_due_date": date | None}

    TODO(backend): POST /api/library/extend  body: {book_id, extra_days}
    """
    for b in _DUMMY_ISSUED_BOOKS:
        if b["book_id"] == book_id:
            if b["renewed"]:
                return {
                    "success": False,
                    "message": "This book has already been renewed once and can't be extended again.",
                    "new_due_date": None,
                }
            b["due_date"] = b["due_date"] + datetime.timedelta(days=extra_days)
            b["renewed"] = True
            return {
                "success": True,
                "message": f"Due date extended to {b['due_date'].strftime('%d %b %Y')}.",
                "new_due_date": b["due_date"],
            }

    return {"success": False, "message": "Book not found.", "new_due_date": None}