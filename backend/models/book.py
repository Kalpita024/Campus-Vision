from database.db import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(80))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="available")  # available / borrowed

    # used by Person 3 (reminders / extensions)
    borrower_name = db.Column(db.String(120))
    borrower_email = db.Column(db.String(120))
    due_date = db.Column(db.Date)
    extension_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "description": self.description,
            "status": self.status,
            "borrower_name": self.borrower_name,
            "borrower_email": self.borrower_email,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "extension_count": self.extension_count,
        }