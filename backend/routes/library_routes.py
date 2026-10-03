"""
routes/library_routes.py
-------------------------
Shared file — Person 2 owns the book/profile endpoints at the top,
Person 3 owns the reminders/extend endpoints at the bottom.

Person 2's endpoints use the SQLAlchemy `Book` model (database/db.py -> db,
models/book.py) and operate on the `books` table.

Person 3's endpoints use raw sqlite3 (database/db.py -> get_connection())
and operate on the `issued_books` table, which is a separate table from
`books`. See the note at the bottom of this file about that mismatch.
"""

import datetime
import sqlite3

from flask import Blueprint, request, jsonify

from database.db import db, get_connection
from models.book import Book

library_bp = Blueprint("library", __name__, url_prefix="/api")


# ===========================================================================
# PERSON 2: books & profile
# ===========================================================================

@library_bp.route("/books", methods=["GET"])
def list_books():
    q = request.args.get("search", "")
    category = request.args.get("category")
    query = Book.query
    if q:
        query = query.filter(Book.title.ilike(f"%{q}%") | Book.author.ilike(f"%{q}%"))
    if category:
        query = query.filter_by(category=category)
    return jsonify([b.to_dict() for b in query.all()]), 200


@library_bp.route("/books", methods=["POST"])
def add_book():
    data = request.get_json() or {}
    for field in ("title", "author", "isbn"):
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    if Book.query.filter_by(isbn=data["isbn"]).first():
        return jsonify({"error": "A book with this ISBN already exists"}), 409

    book = Book(title=data["title"], author=data["author"], isbn=data["isbn"],
                category=data.get("category"), description=data.get("description"))
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@library_bp.route("/books/<int:book_id>", methods=["GET"])
def book_profile(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200


@library_bp.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    data = request.get_json() or {}
    for field in ("title", "author", "category", "description"):
        if field in data:
            setattr(book, field, data[field])
    db.session.commit()
    return jsonify(book.to_dict()), 200


@library_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


# ===========================================================================
# PERSON 3: reminders & extend
# NOTE: these read/write the `issued_books` table (raw sqlite3), which is a
# SEPARATE table from Person 2's `books` table above. The team needs to
# decide whether `issued_books` or `books.borrower_*` fields are the single
# source of truth for "who has which book" — right now both exist. These
# endpoints work correctly against `issued_books` as that table stands.
# ===========================================================================

def _parse_date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["renewed"] = bool(d["renewed"])
    d["returned"] = bool(d["returned"])
    return d


@library_bp.route("/library/reminders/<student_id>", methods=["GET"])
def get_reminders(student_id):
    try:
        window_days = int(request.args.get("window", 3))
    except ValueError:
        return jsonify({"error": "window must be an integer"}), 400

    today = datetime.date.today()

    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM issued_books WHERE student_id = ? AND returned = 0",
        (student_id,),
    ).fetchall()
    conn.close()

    overdue = []
    upcoming = []

    for row in rows:
        book = _row_to_dict(row)
        due = _parse_date(book["due_date"])
        if due < today:
            overdue.append(book)
        elif due <= today + datetime.timedelta(days=window_days):
            upcoming.append(book)

    return jsonify({"overdue": overdue, "upcoming": upcoming}), 200


@library_bp.route("/library/extend", methods=["POST"])
def extend_due_date():
    data = request.get_json(silent=True) or {}
    book_id = data.get("book_id")
    extra_days = data.get("extra_days", 7)

    if not book_id:
        return jsonify({"error": "book_id is required"}), 400

    try:
        extra_days = int(extra_days)
    except (TypeError, ValueError):
        return jsonify({"error": "extra_days must be an integer"}), 400

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM issued_books WHERE book_id = ?", (book_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return jsonify({"error": f"No book found with book_id '{book_id}'"}), 404

    book = _row_to_dict(row)

    if book["renewed"]:
        conn.close()
        return jsonify({
            "success": False,
            "message": "This book has already been renewed once and can't be extended again.",
            "new_due_date": None,
        }), 200

    current_due = _parse_date(book["due_date"])
    new_due = current_due + datetime.timedelta(days=extra_days)

    conn.execute(
        "UPDATE issued_books SET due_date = ?, renewed = 1 WHERE book_id = ?",
        (new_due.strftime("%Y-%m-%d"), book_id),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Due date extended to {new_due.strftime('%d %b %Y')}.",
        "new_due_date": new_due.strftime("%Y-%m-%d"),
    }), 200
