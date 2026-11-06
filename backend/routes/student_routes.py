"""
routes/student_routes.py
------------------------
Roll-number lookup: returns one student's profile, library record and
attendance record. Teachers only. Used by the Student Record page.
"""

from flask import Blueprint, jsonify

from database.db import get_connection
from routes.auth_routes import teacher_required

student_bp = Blueprint("students", __name__)


@student_bp.route("/api/students/by-roll/<roll_no>", methods=["GET"])
@teacher_required
def get_record_by_roll_no(roll_no):
    conn = get_connection()
    try:
        student = conn.execute(
            "SELECT * FROM students WHERE roll_no = ?", (roll_no.strip(),)
        ).fetchone()

        if student is None:
            return jsonify({"error": f"No student found with roll number {roll_no}"}), 404

        student = dict(student)

        books = [
            dict(r) for r in conn.execute(
                "SELECT * FROM issued_books WHERE student_id = ? AND returned = 0",
                (student["student_id"],),
            ).fetchall()
        ]

        attendance = [
            dict(r) for r in conn.execute(
                "SELECT date, subject, status FROM attendance "
                "WHERE student_id = ? ORDER BY date DESC",
                (student["student_id"],),
            ).fetchall()
        ]
    finally:
        conn.close()

    return jsonify({
        "student": student,
        "library": {"issued_books": books},
        "attendance": {"records": attendance},
    })