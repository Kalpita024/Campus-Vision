import sqlite3
import streamlit as st

DB_PATH = "campus.db"  # change to your database path / connection


# ---------- Data access ----------
# `username` is a function argument, so each user gets their own cache entry.
# ttl=30 means data is re-read from the database at most 30 seconds later.
@st.cache_data(ttl=30)
def get_student(username: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT s.id, s.name, s.initials, s.department, s.year,
                   s.student_id, s.email, s.phone, s.membership_valid_till,
                   (SELECT COUNT(*) FROM issued_books b
                     WHERE b.student_id = s.id AND b.returned = 0) AS books_issued
            FROM students s
            WHERE s.username = ?
            """,
            (username,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------- Page ----------
st.title("Library Card")

# 1. Make sure someone is logged in
username = st.session_state.get("username")
if not username:
    st.warning("Please log in to view your library card.")
    st.stop()

# 2. Optional manual refresh button
if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

# 3. Load THIS user's record (no hardcoded ID, no iloc[0])
student = get_student(username)

if student is None:
    st.error(f"No student record found for '{username}'.")
    st.stop()

# 4. Display, with proper label/value separators
st.subheader(student["name"])
st.caption(f"ID: {student['id']}")

st.markdown(
    f"""
**Initials:** {student['initials']}  
**Department:** {student['department']}  
**Year:** {student['year']}  
**Student ID:** {student['student_id']}  
**Email:** {student['email']}  
**Phone:** {student['phone']}  
**Membership valid till:** {student['membership_valid_till']}  
**Books currently issued:** {student['books_issued']}
"""
)

st.caption(
    "This is a digital representation of your library membership card. "
    "Show this at the counter if needed."
)