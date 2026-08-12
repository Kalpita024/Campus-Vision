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
# ---------------------------------------------------------------------------

_DUMMY_ISSUED_BOOKS: List[Dict] = [
    {
        "book_id": "B001",
        "title": "Introduction to Algorithms",
        "author": "Cormen, Leiserson, Rivest, Stein",
        "issue_date": datetime.date(2026, 7, 22),
        "due_date": datetime.date(2026, 8, 9),
        "renewed": False,
        "returned": False,
    },
    {
        "book_id": "B002",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "issue_date": datetime.date(2026, 8, 1),
        "due_date": datetime.date(2026, 8, 13),
        "renewed": False,
        "returned": False,
    },
    {
        "book_id": "B003",
        "title": "Deep Learning",
        "author": "Ian Goodfellow",
        "issue_date": datetime.date(2026, 7, 15),
        "due_date": datetime.date(2026, 8, 25),
        "renewed": False,
        "returned": False,
    },
]

# ---------------------------------------------------------------------------
# DUMMY STUDENT PROFILE
# ---------------------------------------------------------------------------

_DUMMY_STUDENT_PROFILE: Dict = {
    "student_id": "UMIT2026045",
    "name": "Kalpita Naik",
    "roll_no": "45",
    "photo_initials": "KN",
    "department": "AI & Data Science",
    "year": "3rd Year",
    "email": "kalpita.naik@umit.edu.in",
    "phone": "+91 98765 43210",
    "membership_valid_till": datetime.date(2027, 6, 30),
}

# ---------------------------------------------------------------------------
# PUBLIC STUB FUNCTIONS
# ---------------------------------------------------------------------------

def get_student_profile(student_id: str = None) -> Dict:
    """
    Return basic profile info for the digital library card.

    TODO(backend): GET /api/students/<student_id>
    """
    profile = dict(_DUMMY_STUDENT_PROFILE)
    if student_id:
        profile["student_id"] = student_id
    return profile


def get_issued_books(student_id: str) -> List[Dict]:
    """
    Return all currently-issued (not yet returned) books for a student.

    TODO(backend): GET /api/library/issued/<student_id>
    """
    return [b for b in _DUMMY_ISSUED_BOOKS if not b["returned"]]


def get_due_reminders(student_id: str, upcoming_window_days: int = 3) -> Dict[str, List[Dict]]:
    """
    Split issued books into 'overdue' and 'upcoming' (due within
    `upcoming_window_days` days). Used by due_reminders.py to build banners.
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