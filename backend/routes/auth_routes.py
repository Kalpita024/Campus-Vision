"""
routes/auth_routes.py
---------------------
Login endpoint plus the access-control decorators.

Person 2 and Person 3 protect their own endpoints with:
    from routes.auth_routes import teacher_required

    @attendance_bp.route("/api/attendance/mark", methods=["POST"])
    @teacher_required
    def mark_attendance(): ...
"""

from functools import wraps

from flask import Blueprint, current_app, g, jsonify, request
from itsdangerous import BadSignature, URLSafeTimedSerializer
from werkzeug.security import check_password_hash

from database.db import get_connection

auth_bp = Blueprint("auth", __name__)

TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60  # a login lasts 8 hours


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def make_token(user_id: str, role: str) -> str:
    return _serializer().dumps({"user_id": user_id, "role": role})


def get_current_user():
    """Read 'Authorization: Bearer <token>' and return the user, or None."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        return _serializer().loads(header[len("Bearer "):], max_age=TOKEN_MAX_AGE_SECONDS)
    except BadSignature:  # also covers expired tokens
        return None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Login required"}), 401
        g.user = user
        return view(*args, **kwargs)
    return wrapper


def teacher_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Login required"}), 401
        if user["role"] != "teacher":
            return jsonify({"error": "Teachers only"}), 403
        g.user = user
        return view(*args, **kwargs)
    return wrapper


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    role = (data.get("role") or "").strip().lower()
    user_id = (data.get("user_id") or "").strip()

    if role not in ("student", "teacher") or not user_id:
        return jsonify({"error": "role (student/teacher) and user_id are required"}), 400

    conn = get_connection()
    try:
        if role == "student":
            row = conn.execute(
                "SELECT student_id AS user_id, name FROM students WHERE student_id = ?",
                (user_id,),
            ).fetchone()
            if row is None:
                return jsonify({"error": "Student ID is not registered"}), 404
        else:
            row = conn.execute(
                "SELECT user_id, name, password_hash FROM users "
                "WHERE user_id = ? AND role = 'teacher'",
                (user_id,),
            ).fetchone()
            password = data.get("password") or ""
            if row is None or not check_password_hash(row["password_hash"], password):
                return jsonify({"error": "Invalid teacher ID or password"}), 401
    finally:
        conn.close()

    return jsonify({
        "token": make_token(row["user_id"], role),
        "role": role,
        "user_id": row["user_id"],
        "name": row["name"],
    })