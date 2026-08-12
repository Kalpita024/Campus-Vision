"""
Mock data for the Library Management module.
Replace this file with real DB/API calls once the backend is ready —
services/library_api.py is the only place that should import from here.
"""

from datetime import date, timedelta

TODAY = date.today()

# ---------------------------------------------------------------------------
# Dummy logged-in student (later this would come from your auth/session)
# ---------------------------------------------------------------------------
STUDENT_PROFILE = {
    "student_id": "S1001",
    "name": "Aditi Sharma",
    "roll_no": "CS21B045",
    "department": "Computer Science & Engineering",
    "year": "3rd Year",
    "email": "aditi.sharma@campus.edu",
    "phone": "+91 98765 43210",
    "membership_valid_till": TODAY + timedelta(days=180),
    "photo_initials": "AS",  # used as a placeholder avatar since we have no real photo
}

# ---------------------------------------------------------------------------
# Dummy issued/returned books
# ---------------------------------------------------------------------------
DUMMY_BOOKS = [
    {
        "book_id": "B001",
        "title": "Introduction to Algorithms",
        "author": "Thomas H. Cormen",
        "isbn": "978-0262033848",
        "student_id": "S1001",
        "issue_date": TODAY - timedelta(days=12),
        "due_date": TODAY + timedelta(days=2),      # due soon
        "status": "issued",
    },
    {
        "book_id": "B002",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "student_id": "S1001",
        "issue_date": TODAY - timedelta(days=20),
        "due_date": TODAY - timedelta(days=5),      # overdue
        "status": "issued",
    },
    {
        "book_id": "B003",
        "title": "Deep Learning",
        "author": "Ian Goodfellow",
        "isbn": "978-0262035613",
        "student_id": "S1001",
        "issue_date": TODAY - timedelta(days=30),
        "due_date": TODAY + timedelta(days=10),     # comfortably in date
        "status": "issued",
    },
    {
        "book_id": "B004",
        "title": "Computer Networks",
        "author": "Andrew S. Tanenbaum",
        "isbn": "978-0132126953",
        "student_id": "S1001",
        "issue_date": TODAY - timedelta(days=45),
        "due_date": TODAY - timedelta(days=20),
        "status": "returned",                        # already returned
    },
    {
        "book_id": "B005",
        "title": "Database System Concepts",
        "author": "Abraham Silberschatz",
        "isbn": "978-0078022159",
        "student_id": "S1002",                       # belongs to a different student
        "issue_date": TODAY - timedelta(days=8),
        "due_date": TODAY + timedelta(days=6),
        "status": "issued",
    },
]
