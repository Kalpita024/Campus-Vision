"""
database/db.py
--------------
SQLite connection + table creation for CampusVision.

  get_connection()  -> raw sqlite3 connection (rows behave like dicts)
  init_db()         -> creates all tables, the unique roll_no rule, and
                       demo data for development
  db                -> SQLAlchemy object used by the models (books table)
"""

import os
import sqlite3

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "campusvision.db")

db = SQLAlchemy()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name, like a dict
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ---------- STUDENTS ----------
    cur.execute("""
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

    # A roll number must belong to exactly one student
    try:
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_students_roll_no "
            "ON students (roll_no)"
        )
    except sqlite3.IntegrityError:
        print("WARNING: duplicate roll numbers exist in students; fix them first.")

    # ---------- ISSUED BOOKS ----------
    cur.execute("""
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

    # ---------- USERS (teachers) ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'teacher',
            password_hash TEXT NOT NULL
        )
    """)

    # ---------- ATTENDANCE ----------
    # One row per student, per date, per subject
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            subject TEXT NOT NULL DEFAULT 'general',
            status TEXT NOT NULL DEFAULT 'present',
            marked_by TEXT,
            UNIQUE (student_id, date, subject),
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    """)

    # ---------- DEMO DATA (development only) ----------
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, name, role, password_hash) "
        "VALUES (?, ?, ?, ?)",
        ("TCH001", "Demo Teacher", "teacher", generate_password_hash("teacher123")),
    )

    cur.execute(
        "INSERT OR IGNORE INTO students "
        "(student_id, name, roll_no, photo_initials, department, year, "
        " email, phone, membership_valid_till) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("UMIT2026045", "Kalpita Naik", "45", "KN", "AI & Data Science",
         "3rd Year", "kalpita.naik@umit.edu.in", "+91 98765 43210",
         "2027-06-30"),
    )

    demo_books = [
        ("B001", "UMIT2026045", "Introduction to Algorithms",
         "Cormen, Leiserson, Rivest, Stein", "2026-10-20", "2026-11-09"),
        ("B002", "UMIT2026045", "Clean Code",
         "Robert C. Martin", "2026-10-28", "2026-11-12"),
        ("B003", "UMIT2026045", "Deep Learning",
         "Ian Goodfellow", "2026-10-15", "2026-11-25"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO issued_books "
        "(book_id, student_id, title, author, issue_date, due_date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        demo_books,
    )

    conn.commit()
    conn.close()
