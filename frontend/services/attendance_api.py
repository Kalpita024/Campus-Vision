"""
services/attendance_api.py
 
Data layer for attendance. Uses a local SQLite file (data/attendance.db) so the
app works out of the box with no server.
 
If you later get a real backend (Flask/FastAPI/etc.), keep the same function
names/signatures and replace the bodies with `requests.get/post(...)` calls.
Your Streamlit pages won't need to change.
"""
 
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
 
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "attendance.db"
 
PRESENT = "Present"
ABSENT = "Absent"
 
 
@contextmanager
def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()
 
 
def init_db():
    with _conn() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                class_name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS attendance (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                date       TEXT NOT NULL,
                class_name TEXT NOT NULL,
                subject    TEXT NOT NULL,
                student_id TEXT NOT NULL,
                status     TEXT NOT NULL,
                UNIQUE (date, class_name, subject, student_id)
            );
            """
        )
 
 
init_db()
 
 
# ------------------------------- Students ---------------------------------- #
def add_student(student_id: str, name: str, class_name: str):
    """Insert or update a student (called by tools/enroll_faces.py)."""
    with _conn() as con:
        con.execute(
            """INSERT INTO students (student_id, name, class_name) VALUES (?, ?, ?)
               ON CONFLICT(student_id) DO UPDATE SET name=excluded.name,
                                                     class_name=excluded.class_name""",
            (student_id, name, class_name),
        )
 
 
def get_classes():
    with _conn() as con:
        rows = con.execute("SELECT DISTINCT class_name FROM students ORDER BY class_name")
        return [r["class_name"] for r in rows]
 
 
def get_students(class_name: str | None = None):
    """Return list of dicts: student_id, name, class_name."""
    with _conn() as con:
        if class_name:
            rows = con.execute(
                "SELECT * FROM students WHERE class_name=? ORDER BY name", (class_name,)
            )
        else:
            rows = con.execute("SELECT * FROM students ORDER BY class_name, name")
        return [dict(r) for r in rows]
 
 
# ------------------------------ Attendance --------------------------------- #
def mark_attendance(class_name: str, subject: str, records: dict, on_date: date | None = None):
    """
    records = {"S101": "Present", "S102": "Absent", ...}
    Re-submitting for the same date/class/subject overwrites the earlier entry.
    """
    on_date = (on_date or date.today()).isoformat()
    with _conn() as con:
        con.executemany(
            """INSERT INTO attendance (date, class_name, subject, student_id, status)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(date, class_name, subject, student_id)
               DO UPDATE SET status=excluded.status""",
            [(on_date, class_name, subject, sid, status) for sid, status in records.items()],
        )
 
 
def get_attendance(class_name: str | None = None, subject: str | None = None,
                   on_date: date | None = None, student_id: str | None = None):
    """Flexible filter, returns list of dicts (useful for the history/status pages)."""
    query = (
        "SELECT a.date, a.class_name, a.subject, a.student_id, s.name, a.status "
        "FROM attendance a LEFT JOIN students s ON s.student_id = a.student_id WHERE 1=1"
    )
    params = []
    if class_name:
        query += " AND a.class_name=?"; params.append(class_name)
    if subject:
        query += " AND a.subject=?"; params.append(subject)
    if on_date:
        query += " AND a.date=?"; params.append(on_date.isoformat())
    if student_id:
        query += " AND a.student_id=?"; params.append(student_id)
    query += " ORDER BY a.date DESC, s.name"
    with _conn() as con:
        return [dict(r) for r in con.execute(query, params)]
 
 
def get_attendance_percentage(student_id: str):
    """Overall % for a student (handy for Defaulters / Student Record pages)."""
    with _conn() as con:
        row = con.execute(
            """SELECT COUNT(*) AS total,
                      SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present
               FROM attendance WHERE student_id=?""",
            (student_id,),
        ).fetchone()
    if not row["total"]:
        return 0.0
    return round(100 * (row["present"] or 0) / row["total"], 1)
 