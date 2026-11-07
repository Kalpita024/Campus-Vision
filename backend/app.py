import os

from flask import Flask

from database.db import init_db, db
from routes.library_routes import library_bp
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.defaulter_routes import defaulter_bp

app = Flask(__name__)

# Signs login tokens. Set a real value in production, never commit it.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campusvision.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.register_blueprint(library_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(defaulter_bp)


@app.route("/")
def home():
    return {"message": "CampusVision backend is running"}


if __name__ == "__main__":
    init_db()
    with app.app_context():
        db.create_all()  # creates the books table (SQLAlchemy)
    app.run(debug=True, port=5000)