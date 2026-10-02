from flask import Blueprint, request, jsonify
from database.db import db
from models.book import Book

library_bp = Blueprint("library", __name__, url_prefix="/api")

# ---- Person 2: books & profile ----

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