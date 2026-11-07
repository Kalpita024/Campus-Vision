"""
models/attendance.py  -- PERSON 2

Owns the `attendance` table. Other modules should only READ it:
  * Person 3 (services/attendance_calc.py, routes/defaulter_routes.py)
    -> use get_subject_counts(), get_all_subject_counts(), get_subjects()
  * Person 1 (routes/student_routes.py, pages/8_Student_Record.py)
    -> use get_student_attendance()

Works with database/db.py (Person 1):
  * get_connection()  -> a NEW sqlite3 connection with row_factory = sqlite3.Row
  * students table    -> student_id (TEXT, e.g. UMIT2026045), name, roll_no
  * attendance table  -> created by db.py; create_table() below adds the extra
                         columns this module needs (method, marked_at).
"""
from datetime import datetime

from database.db import get_connection as get_db

VALID_STATUSES = ("Present", "Absent")
VALID_METHODS = ("face", "manual")


def _rows(cursor):
    return [dict(r) for r in cursor.fetchall()]


# ------------------------------------------------------------------ schema
def create_table():
    """
    Call once at startup, after init_db() (see backend/app.py).

    db.py already creates the base `attendance` table. This makes sure it
    exists and adds the two extra columns this module uses, if missing.
    Safe to run every time.
    """
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT    NOT NULL,
                date       TEXT    NOT NULL,              -- YYYY-MM-DD
                subject    TEXT    NOT NULL DEFAULT 'general',
                status     TEXT    NOT NULL DEFAULT 'Present',
                marked_by  TEXT,
                UNIQUE (student_id, date, subject),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)

        existing = {row["name"] for row in conn.execute("PRAGMA table_info(attendance)")}
        if "method" not in existing:
            conn.execute("ALTER TABLE attendance ADD COLUMN method TEXT NOT NULL DEFAULT 'face'")
        if "marked_at" not in existing:
            conn.execute("ALTER TABLE attendance ADD COLUMN marked_at TEXT")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_student ON attendance(student_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_date ON attendance(date)")
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------ writes
def mark_attendance(student_id, subject, date, status="Present", method="face", marked_by=None):
    """Insert or update (one record per student/subject/date). Returns the row."""
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO attendance (student_id, date, subject, status, method, marked_at, marked_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, date, subject)
            DO UPDATE SET status = excluded.status,
                          method = excluded.method,
                          marked_at = excluded.marked_at,
                          marked_by = excluded.marked_by
        """, (student_id, date, subject, status, method, now, marked_by))
        conn.commit()
        cur = conn.execute(
            "SELECT * FROM attendance WHERE student_id=? AND subject=? AND date=?",
            (student_id, subject, date))
        return dict(cur.fetchone())
    finally:
        conn.close()


def update_status(attendance_id, status, marked_by=None):
    conn = get_db()
    try:
        cur = conn.execute(
            "UPDATE attendance SET status=?, method='manual', marked_by=? WHERE id=?",
            (status, marked_by, attendance_id))
        conn.commit()
        if cur.rowcount == 0:
            return None
        return dict(conn.execute("SELECT * FROM attendance WHERE id=?",
                                 (attendance_id,)).fetchone())
    finally:
        conn.close()


def delete_attendance(attendance_id):
    conn = get_db()
    try:
        cur = conn.execute("DELETE FROM attendance WHERE id=?", (attendance_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ------------------------------------------------------------------ reads
def get_student_id_by_roll(roll_no):
    conn = get_db()
    try:
        row = conn.execute("SELECT student_id FROM students WHERE roll_no=?", (roll_no,)).fetchone()
        return row["student_id"] if row else None
    finally:
        conn.close()


def student_exists(student_id):
    conn = get_db()
    try:
        return conn.execute("SELECT 1 FROM students WHERE student_id=?", (student_id,)).fetchone() is not None
    finally:
        conn.close()


def get_student_attendance(student_id, subject=None, date_from=None, date_to=None):
    """History of one student, newest first. Used by Person 1 and Person 3 pages."""
    sql = "SELECT * FROM attendance WHERE student_id=?"
    params = [student_id]
    if subject:
        sql += " AND subject=?"; params.append(subject)
    if date_from:
        sql += " AND date>=?"; params.append(date_from)
    if date_to:
        sql += " AND date<=?"; params.append(date_to)
    sql += " ORDER BY date DESC, id DESC"
    conn = get_db()
    try:
        return _rows(conn.execute(sql, params))
    finally:
        conn.close()


def get_by_date(date, subject=None):
    """All records for a day, joined with student info."""
    sql = """SELECT a.*, s.name, s.roll_no
             FROM attendance a JOIN students s ON s.student_id = a.student_id
             WHERE a.date=?"""
    params = [date]
    if subject:
        sql += " AND a.subject=?"; params.append(subject)
    sql += " ORDER BY s.roll_no"
    conn = get_db()
    try:
        return _rows(conn.execute(sql, params))
    finally:
        conn.close()


def get_session_status(date, subject):
    """Marked / not-yet-marked lists for one class session (Take Attendance page)."""
    conn = get_db()
    try:
        marked = _rows(conn.execute("""
            SELECT s.student_id, s.name, s.roll_no, a.status, a.marked_at
            FROM students s JOIN attendance a ON a.student_id = s.student_id
            WHERE a.date=? AND a.subject=? ORDER BY s.roll_no""", (date, subject)))
        unmarked = _rows(conn.execute("""
            SELECT s.student_id, s.name, s.roll_no FROM students s
            WHERE s.student_id NOT IN (SELECT student_id FROM attendance WHERE date=? AND subject=?)
            ORDER BY s.roll_no""", (date, subject)))
        return {"marked": marked, "unmarked": unmarked}
    finally:
        conn.close()


def get_subjects():
    conn = get_db()
    try:
        return [r["subject"] for r in conn.execute(
            "SELECT DISTINCT subject FROM attendance ORDER BY subject")]
    finally:
        conn.close()


# ---- helpers for Person 3 (percentages are THEIR job; we only give raw counts)
def get_subject_counts(student_id):
    """[{subject, total, present}] for one student."""
    conn = get_db()
    try:
        return _rows(conn.execute("""
            SELECT subject, COUNT(*) AS total,
                   SUM(CASE WHEN LOWER(status)='present' THEN 1 ELSE 0 END) AS present
            FROM attendance WHERE student_id=? GROUP BY subject""", (student_id,)))
    finally:
        conn.close()


def get_all_subject_counts():
    """[{student_id, name, roll_no, subject, total, present}] for every student."""
    conn = get_db()
    try:
        return _rows(conn.execute("""
            SELECT s.student_id AS student_id, s.name, s.roll_no, a.subject,
                   COUNT(*) AS total,
                   SUM(CASE WHEN LOWER(a.status)='present' THEN 1 ELSE 0 END) AS present
            FROM attendance a JOIN students s ON s.student_id = a.student_id
            GROUP BY s.student_id, a.subject ORDER BY s.roll_no"""))
    finally:
        conn.close()
