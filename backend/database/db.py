import sqlite3
import os

from flask_sqlalchemy import SQLAlchemy

DB_PATH = os.path.join(os.path.dirname(__file__), "campusvision.db")

# ---------------------------------------------------------------------------
# Raw sqlite3 connection — used by Person 1 (setup) and Person 3
# (reminders/extend endpoints), on the `students` and `issued_books` tables.
# ---------------------------------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, like a dict
    return conn


def init_db():
    conn = get_connection()
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


# ---------------------------------------------------------------------------
# SQLAlchemy object — used by Person 2's models/book.py (the `books` table).
# Points at the SAME campusvision.db file as the raw-sqlite3 code above.
# Call db.init_app(app) and db.create_all() in app.py (see app.py).
# ---------------------------------------------------------------------------

db = SQLAlchemy()