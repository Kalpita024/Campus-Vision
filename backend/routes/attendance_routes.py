"""
routes/attendance_routes.py  -- PERSON 2

Register in app.py:
    from routes.attendance_routes import attendance_bp
    app.register_blueprint(attendance_bp)        # served under /api/attendance

Called from the frontend by services/attendance_api.py.
"""
from datetime import date as _date, datetime
from flask import Blueprint, request, jsonify
from models import attendance as att

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")


def _ok(data=None, message="OK", code=200):
    return jsonify({"success": True, "message": message, "data": data}), code


def _err(message, code=400):
    return jsonify({"success": False, "message": message, "data": None}), code


def _valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def _resolve_student_id(body):
    """Accept either student_id or roll_no."""
    if body.get("student_id") is not None:
        return int(body["student_id"])
    if body.get("roll_no"):
        return att.get_student_id_by_roll(str(body["roll_no"]))
    return None


def _clean(body):
    """Validate shared fields. Returns (values, error_message)."""
    subject = (body.get("subject") or "").strip()
    if not subject:
        return None, "subject is required"
    day = body.get("date") or _date.today().isoformat()
    if not _valid_date(day):
        return None, "date must be YYYY-MM-DD"
    status = body.get("status", "Present")
    if status not in att.VALID_STATUSES:
        return None, f"status must be one of {att.VALID_STATUSES}"
    method = body.get("method", "face")
    if method not in att.VALID_METHODS:
        return None, f"method must be one of {att.VALID_METHODS}"
    return {"subject": subject, "date": day, "status": status, "method": method}, None


# ---------------------------------------------------------------- mark
@attendance_bp.route("/mark", methods=["POST"])
def mark():
    """Body: {student_id | roll_no, subject, date?, status?, method?}"""
    body = request.get_json(silent=True) or {}
    vals, error = _clean(body)
    if error:
        return _err(error)
    try:
        student_id = _resolve_student_id(body)
    except (TypeError, ValueError):
        return _err("student_id must be an integer")
    if student_id is None or not att.student_exists(student_id):
        return _err("Student not found", 404)

    record = att.mark_attendance(student_id, **vals)
    return _ok(record, "Attendance marked", 201)


@attendance_bp.route("/mark-bulk", methods=["POST"])
def mark_bulk():
    """Body: {students: [id or roll_no, ...], subject, date?, status?, method?}
    Used by face recognition when several faces are detected in one frame."""
    body = request.get_json(silent=True) or {}
    vals, error = _clean(body)
    if error:
        return _err(error)
    students = body.get("students")
    if not isinstance(students, list) or not students:
        return _err("students must be a non-empty list")

    marked, not_found = [], []
    for s in students:
        key = {"student_id": s} if isinstance(s, int) else {"roll_no": s}
        sid = _resolve_student_id(key)
        if sid is None or not att.student_exists(sid):
            not_found.append(s)
            continue
        marked.append(att.mark_attendance(sid, **vals))
    return _ok({"marked": marked, "not_found": not_found},
               f"{len(marked)} marked, {len(not_found)} not found")


# ---------------------------------------------------------------- read
@attendance_bp.route("/student/<int:student_id>", methods=["GET"])
def student_history(student_id):
    """Query: subject?, from?, to?"""
    if not att.student_exists(student_id):
        return _err("Student not found", 404)
    date_from, date_to = request.args.get("from"), request.args.get("to")
    for d in (date_from, date_to):
        if d and not _valid_date(d):
            return _err("from/to must be YYYY-MM-DD")
    rows = att.get_student_attendance(student_id, request.args.get("subject"), date_from, date_to)
    return _ok(rows)


@attendance_bp.route("/student/<int:student_id>/counts", methods=["GET"])
def student_counts(student_id):
    """Raw present/total per subject (percentages are computed by Person 3)."""
    if not att.student_exists(student_id):
        return _err("Student not found", 404)
    return _ok(att.get_subject_counts(student_id))


@attendance_bp.route("/date/<day>", methods=["GET"])
def by_date(day):
    """Query: subject?"""
    if not _valid_date(day):
        return _err("date must be YYYY-MM-DD")
    return _ok(att.get_by_date(day, request.args.get("subject")))


@attendance_bp.route("/session", methods=["GET"])
def session_status():
    """Query: subject (required), date? (default today). Returns marked/unmarked lists."""
    subject = (request.args.get("subject") or "").strip()
    day = request.args.get("date") or _date.today().isoformat()
    if not subject:
        return _err("subject is required")
    if not _valid_date(day):
        return _err("date must be YYYY-MM-DD")
    return _ok(att.get_session_status(day, subject))


@attendance_bp.route("/subjects", methods=["GET"])
def subjects():
    return _ok(att.get_subjects())


# ---------------------------------------------------------------- edit / delete
@attendance_bp.route("/<int:attendance_id>", methods=["PUT"])
def edit(attendance_id):
    """Body: {status}  (manual correction)"""
    body = request.get_json(silent=True) or {}
    status = body.get("status")
    if status not in att.VALID_STATUSES:
        return _err(f"status must be one of {att.VALID_STATUSES}")
    record = att.update_status(attendance_id, status)
    if record is None:
        return _err("Record not found", 404)
    return _ok(record, "Updated")


@attendance_bp.route("/<int:attendance_id>", methods=["DELETE"])
def remove(attendance_id):
    if not att.delete_attendance(attendance_id):
        return _err("Record not found", 404)
    return _ok(None, "Deleted")