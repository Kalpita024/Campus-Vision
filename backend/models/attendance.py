"""
models/attendance.py  -- PERSON 2

Owns the `attendance` table. Other modules should only READ it:
  * Person 3 (services/attendance_calc.py, routes/defaulter_routes.py)
    -> use get_subject_counts(), get_all_subject_counts(), get_subjects()
  * Person 1 (routes/student_routes.py, pages/8_Student_Record.py)
    -> use get_student_attendance()

Assumes database/db.py (Person 1) exposes:
    get_db()  -> a NEW sqlite3 connection with row_factory = sqlite3.Row
and a `students` table with columns: id, roll_no, name.
"""
from datetime import datetime
from database.db import get_db

VALID_STATUSES = ("Present", "Absent")
VALID_METHODS = ("face", "manual")


def _rows(cursor):
    return [dict(r) for r in cursor.fetchall()]


# ------------------------------------------------------------------ schema
def create_table():
    """Call once at startup (from database/db.py init_db() or app.py)."""
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject    TEXT    NOT NULL,
                date       TEXT    NOT NULL,              -- YYYY-MM-DD
                status     TEXT    NOT NULL DEFAULT 'Present',
                method     TEXT    NOT NULL DEFAULT 'face',
                marked_at  TEXT    NOT NULL,
                UNIQUE (student_id, subject, date),
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_student ON attendance(student_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_date ON attendance(date)")
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------ writes
def mark_attendance(student_id, subject, date, status="Present", method="face"):
    """Insert or update (one record per student/subject/date). Returns the row."""
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO attendance (student_id, subject, date, status, method, marked_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, subject, date)
            DO UPDATE SET status = excluded.status,
                          method = excluded.method,
                          marked_at = excluded.marked_at
        """, (student_id, subject, date, status, method, now))
        conn.commit()
        cur = conn.execute(
            "SELECT * FROM attendance WHERE student_id=? AND subject=? AND date=?",
            (student_id, subject, date))
        return dict(cur.fetchone())
    finally:
        conn.close()


def update_status(attendance_id, status):
    conn = get_db()
    try:
        cur = conn.execute("UPDATE attendance SET status=?, method='manual' WHERE id=?",
                           (status, attendance_id))
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
        row = conn.execute("SELECT id FROM students WHERE roll_no=?", (roll_no,)).fetchone()
        return row["id"] if row else None
    finally:
        conn.close()


def student_exists(student_id):
    conn = get_db()
    try:
        return conn.execute("SELECT 1 FROM students WHERE id=?", (student_id,)).fetchone() is not None
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
             FROM attendance a JOIN students s ON s.id = a.student_id
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
    """Present / not-yet-marked lists for one class session (Take Attendance page)."""
    conn = get_db()
    try:
        present = _rows(conn.execute("""
            SELECT s.id, s.name, s.roll_no, a.status, a.marked_at
            FROM students s JOIN attendance a ON a.student_id = s.id
            WHERE a.date=? AND a.subject=? ORDER BY s.roll_no""", (date, subject)))
        unmarked = _rows(conn.execute("""
            SELECT s.id, s.name, s.roll_no FROM students s
            WHERE s.id NOT IN (SELECT student_id FROM attendance WHERE date=? AND subject=?)
            ORDER BY s.roll_no""", (date, subject)))
        return {"marked": present, "unmarked": unmarked}
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
                   SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present
            FROM attendance WHERE student_id=? GROUP BY subject""", (student_id,)))
    finally:
        conn.close()


def get_all_subject_counts():
    """[{student_id, name, roll_no, subject, total, present}] for every student."""
    conn = get_db()
    try:
        return _rows(conn.execute("""
            SELECT s.id AS student_id, s.name, s.roll_no, a.subject,
                   COUNT(*) AS total,
                   SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present
            FROM attendance a JOIN students s ON s.id = a.student_id
            GROUP BY s.id, a.subject ORDER BY s.roll_no"""))
    finally:
        conn.close()