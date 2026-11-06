# CampusVision

Smart Campus Management System: a mini project combining a digital library
management system and face recognition attendance.

## Team
- Hindavi Bhopi
- Kalpita Naik
- Shraddha Tripathi

Guided by Prof. Supriya Ingale, B.Tech (AI), Usha Mittal Institute of Technology,
SNDT Women's University.

## Features

**Library module**
- Digital library card
- Issued books list with due-date status (on time / due soon / overdue)
- Due-date reminders
- Renew (extend) a due date from the app

**Attendance module**
- Face detection and recognition using OpenCV Haar cascades
- Attendance marked by teachers only
- Attendance percentage and exam eligibility
- Defaulter list for teachers and alerts for students

**Access and lookup**
- Two roles: Student and Teacher, with role-based pages
- Teachers can look up any student's library and attendance record by roll number

## Tech Stack
- Frontend: Python + Streamlit
- Backend: Flask + SQLite (SQLAlchemy for the books model)
- Face recognition: OpenCV (Haar cascade detection) with Tkinter for recording face data

## Project Structure
```
frontend/
├── app.py                  Login (Student / Teacher)
├── pages/                  Dashboard, Library Card, Issued Books,
│                           Attendance pages, Defaulters, Student Record
├── components/             navbar.py and shared components
├── services/               API calls to the backend
└── utils/                  Shared styling

backend/
├── app.py                  Server entry point
├── database/db.py          SQLite connection and tables
├── routes/                 auth, student lookup, library, attendance, defaulters
├── models/                 Data models
└── requirements.txt
```

## How to Run

Install the dependencies:
```
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

Start the backend (in its own terminal):
```
cd backend
python app.py
```

Start the frontend (in a second terminal):
```
cd frontend
python -m streamlit run app.py
```

The backend runs at http://127.0.0.1:5000 and the frontend at http://localhost:8501.
If the backend is not running, the frontend falls back to demo mode with dummy data.

## Demo Logins (development only)
| Role | ID | Password |
|---|---|---|
| Teacher | TCH001 | teacher123 |
| Student | UMIT2026045 | (no password) |

These are demo accounts for development and testing. Replace them before any real use.

## Notes
- Set a real `SECRET_KEY` environment variable for the backend in production.
- The database file (`backend/database/campusvision.db`) is created automatically
  on first run and is not committed to Git.