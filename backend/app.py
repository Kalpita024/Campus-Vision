from flask import Flask
from database.db import init_db, db
from routes.library_routes import library_bp

app = Flask(__name__)

# Point SQLAlchemy at the same campusvision.db file the raw-sqlite3 code uses
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campusvision.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.register_blueprint(library_bp)


@app.route("/")
def home():
    return {"message": "CampusVision backend is running"}


if __name__ == "__main__":
    init_db()  # creates students + issued_books tables (raw sqlite3)
    with app.app_context():
        db.create_all()  # creates the books table (SQLAlchemy)
    app.run(debug=True, port=5000)
