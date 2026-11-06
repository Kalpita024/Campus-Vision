"""
routes/defaulter_routes.py  -- PERSON 3
---------------------------------------
Register in app.py:
    from routes.defaulter_routes import defaulter_bp
    app.register_blueprint(defaulter_bp)

GET /api/defaulters                      (teachers only)
    Query: threshold (default 75), subject?, class?, include_all? (1 = every student)
GET /api/attendance-summary/<student_id> (login needed; a student sees only their own)
    Query: threshold (default 75)

Reads the `attendance` and `students` tables directly. Status is compared
case-insensitively, so 'present' and 'Present' both count as present.
"""

from flask import Blueprint, g, jsonify, request

from database.db import get_connection
from routes.auth_routes import login_required, teacher_required
from services.attendance_calc import ATTENDANCE_THRESHOLD, summarise

defaulter_bp = Blueprint("defaulters", __name__)

_PRESENT = "LOWER(a.status) = 'present'"


def _threshold():
    """Read ?threshold=, keep it between 1 and 99."""
    try:
        value = int(request.args.get("threshold", ATTENDANCE_THRESHOLD))
    except ValueError:
        return None
    return value if 1 <= value <= 99 else None


def _class_name(row):
    """The students table has no class column, so build one from year + department."""
    parts = [p for p in (row["year"], row["department"]) if p]
    return " ".join(parts) if parts else None


@defaulter_bp.route("/api/defaulters", methods=["GET"])
@teacher_required
def list_defaulters():
    threshold = _threshold()
    if threshold is None:
        return jsonify({"error": "threshold must be a whole number from 1 to 99"}), 400

    subject = (request.args.get("subject") or "").strip()
    class_filter = (request.args.get("class") or "").strip()
    include_all = request.args.get("include_all") == "1"

    sql = f"""
        SELECT s.student_id, s.name, s.roll_no, s.year, s.department,
               COUNT(*) AS total,
               SUM(CASE WHEN {_PRESENT} THEN 1 ELSE 0 END) AS attended
        FROM attendance a JOIN students s ON s.student_id = a.student_id
        {"WHERE a.subject = ?" if subject else ""}
        GROUP BY s.student_id
    """
    conn = get_connection()
    try:
        rows = conn.execute(sql, [subject] if subject else []).fetchall()
    finally:
        conn.close()

    students = []
    for r in rows:
        cls = _class_name(r)
        if class_filter and cls != class_filter:
            continue
        item = {
            "student_id": r["student_id"],
            "name": r["name"],
            "roll_no": r["roll_no"],
            "class_name": cls,
            **summarise(r["attended"] or 0, r["total"], threshold),
        }
        if include_all or item["status"] == "defaulter":
            students.append(item)

    students.sort(key=lambda s: s["percentage"])
    return jsonify({
        "threshold": threshold,
        "count": len(students),
        "students": students,
    })


@defaulter_bp.route("/api/attendance-summary/<student_id>", methods=["GET"])
@login_required
def attendance_summary(student_id):
    user = g.user
    if user["role"] == "student" and user["user_id"] != student_id:
        return jsonify({"error": "You can only view your own attendance"}), 403

    threshold = _threshold()
    if threshold is None:
        return jsonify({"error": "threshold must be a whole number from 1 to 99"}), 400

    conn = get_connection()
    try:
        if conn.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,)).fetchone() is None:
            return jsonify({"error": "Student not found"}), 404
        rows = conn.execute(
            f"""SELECT a.subject, COUNT(*) AS total,
                       SUM(CASE WHEN {_PRESENT} THEN 1 ELSE 0 END) AS attended
                FROM attendance a WHERE a.student_id = ? GROUP BY a.subject
                ORDER BY a.subject""",
            (student_id,),
        ).fetchall()
    finally:
        conn.close()

    subjects = [
        {"subject": r["subject"], **summarise(r["attended"] or 0, r["total"], threshold)}
        for r in rows
    ]
    attended = sum(s["attended"] for s in subjects)
    total = sum(s["total"] for s in subjects)
    return jsonify({
        "student_id": student_id,
        "threshold": threshold,
        "overall": summarise(attended, total, threshold),
        "subjects": subjects,
    })
