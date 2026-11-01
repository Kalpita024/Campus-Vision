import sqlite3
from pathlib import Path
import streamlit as st


# ---------- Database path ----------
# Use the SAME database as backend/database/db.py
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "backend" / "database" / "campusvision.db"


# ---------- Initialize database ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            roll_no TEXT,
            photo_initials TEXT,
            department TEXT,
            year TEXT,
            email TEXT,
            phone TEXT,
            membership_valid_till TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            book_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            renewed INTEGER DEFAULT 0,
            returned INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    """)

    conn.commit()
    conn.close()


# Make sure tables exist
init_db()


# ---------- Get student ----------
def get_student(student_id: str):
    """Returns (student_dict_or_None, error_message_or_None)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        try:
            row = conn.execute(
                "SELECT * FROM students WHERE student_id = ?",
                (student_id,),
            ).fetchone()
        finally:
            conn.close()

        return (dict(row) if row else None), None

    except sqlite3.Error as e:
        return None, str(e)


# ---------- Get issued books ----------
def get_books_issued(student_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)

        try:
            count = conn.execute(
                """
                SELECT COUNT(*)
                FROM issued_books
                WHERE student_id = ?
                AND returned = 0
                """,
                (student_id,),
            ).fetchone()[0]

        finally:
            conn.close()

        return count

    except sqlite3.Error:
        return "-"


# ---------- Page ----------
st.title("Library Card")


# 1. Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please log in from the main page to view your library card.")
    st.stop()


student_id = st.session_state.get("student_id", "")
student_name = st.session_state.get("student_name", "")


# 2. Load student details
record, error = get_student(student_id)
record = record or {}


# 3. Build card
name = record.get("name") or student_name
department = record.get("department", "-")
year = record.get("year", "-")
email = record.get("email", "-")
phone = record.get("phone", "-")
valid_till = record.get("membership_valid_till", "-")

books_issued = get_books_issued(student_id)


# 4. Display card
st.subheader(name)

st.caption(f"Student ID: {student_id}")

st.markdown(
    f"""
**Name:** {name}  
**Department:** {department}  
**Year:** {year}  
**Student ID:** {student_id}  
**Email:** {email}  
**Phone:** {phone}  
**Membership valid till:** {valid_till}  
**Books currently issued:** {books_issued}
"""
)


st.caption(
    "This is a digital representation of your library membership card. "
    "Show this at the counter if needed."
)


# 5. Helpful messages
if error:
    st.info(f"Showing basic details only. Database message: {error}")

elif not record:
    st.info(
        "No extra details found for this Student ID in the database yet."
    )