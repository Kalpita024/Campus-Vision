import streamlit as st
from components.navbar import render_navbar
from services.library_api import (
    get_student_profile,
    get_issued_books,
    get_book_status,
    days_remaining,
)

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Student Record - CampusVision",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

render_navbar("Student Record")

# ---------- ACCESS GUARDS ----------
if not st.session_state.get("logged_in", False):
    st.warning("Please log in first from the Home page.")
    st.stop()

if st.session_state.get("role") != "teacher":
    st.error("This page is only available to teachers.")
    st.stop()

# ---------- CUSTOM STYLING (same theme as app.py) ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Jost', sans-serif;
    }

    .stApp {
        background: #F5F1EA;
    }

    .block-container {
        padding-top: 2.5rem;
    }

    .hero {
        background: #FFFFFF;
        padding: 2.2rem 1.5rem 1.7rem 1.5rem;
        border-radius: 4px;
        text-align: center;
        border: 1px solid #E4DCCB;
        border-bottom: 3px solid #A88B5A;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-family: 'Cormorant Garamond', serif;
        color: #3B3226;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 1px;
    }
    .hero p {
        font-family: 'Jost', sans-serif;
        color: #8A7B60;
        font-size: 0.9rem;
        margin-top: 0.4rem;
        margin-bottom: 0;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border-radius: 4px;
        border: 1px solid #E4DCCB !important;
    }

    .section-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #3B3226;
        margin-bottom: 0.6rem;
    }

    .student-name {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #3B3226;
        margin: 0;
    }
    .student-meta {
        color: #8A7B60;
        font-size: 0.9rem;
        margin: 0;
    }

    .book-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #3B3226;
        margin: 0;
    }
    .book-meta {
        color: #A69B85;
        font-size: 0.85rem;
        margin: 0;
    }

    .tag {
        display: inline-block;
        font-size: 0.72rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 0.15rem 0.55rem;
        border-radius: 2px;
        margin-top: 0.3rem;
    }
    .tag-ok      { background: #EEF3E6; color: #55703A; }
    .tag-soon    { background: #F8F0DA; color: #8A6D1F; }
    .tag-overdue { background: #F6E3DF; color: #9A3B2B; }

    div[data-testid="stTextInput"] input {
        border-radius: 2px;
        border: 1px solid #D8CDB8;
        background-color: #FBF9F5;
        padding: 0.65rem 0.9rem;
        color: #3B3226;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #A88B5A;
        box-shadow: 0 0 0 1px #A88B5A;
        background-color: #FFFFFF;
    }
    div[data-testid="stTextInput"] label {
        font-weight: 500;
        color: #6B6152;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .stButton>button {
        width: 100%;
        background: #3B3226;
        color: #F5F1EA;
        border-radius: 2px;
        padding: 0.65rem 0;
        font-weight: 500;
        font-size: 0.95rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border: none;
        transition: background 0.2s ease;
    }
    .stButton>button:hover {
        background: #A88B5A;
        color: #FFFFFF;
    }

    div[data-testid="stAlert"] {
        border-radius: 2px;
    }
    </style>
""", unsafe_allow_html=True)


# ---------- LOOKUP HELPER ----------
def find_student_by_roll_no(roll_no: str):
    """
    Return the student whose roll number matches, or None.

    TODO(backend): replace with a real call to the lookup endpoint
    (roll no. -> student), once routes/student_routes.py exists.
    For now only the one dummy student in library_api.py can be found.
    """
    student = get_student_profile()
    if student["roll_no"].strip() == roll_no.strip():
        return student
    return None


# ---------- HERO HEADER ----------
st.markdown("""
    <div class="hero">
        <h1>Student Record</h1>
        <p>Look up a student by roll number</p>
    </div>
""", unsafe_allow_html=True)

# ---------- SEARCH BOX ----------
with st.container(border=True):
    roll_no = st.text_input("Roll Number", placeholder="e.g. 45")
    search_clicked = st.button("Search")

# Remember the last search so the page doesn't reset on every click
if search_clicked:
    if not roll_no.strip():
        st.session_state.record_roll_no = ""
        st.error("Please enter a roll number.")
    else:
        st.session_state.record_roll_no = roll_no.strip()

searched_roll_no = st.session_state.get("record_roll_no", "")

# ---------- RESULTS ----------
if searched_roll_no:
    student = find_student_by_roll_no(searched_roll_no)

    if student is None:
        st.error(f"No student found with roll number {searched_roll_no}.")
    else:
        st.write("")

        # Student info card
        with st.container(border=True):
            st.markdown(f'<p class="student-name">{student["name"]}</p>', unsafe_allow_html=True)
            st.markdown(
                f'<p class="student-meta">Roll No. {student["roll_no"]} · '
                f'{student["department"]} · {student["year"]}</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p class="student-meta">Student ID: {student["student_id"]}</p>',
                unsafe_allow_html=True,
            )

        st.write("")
        tab_library, tab_attendance = st.tabs(["📚 Library Record", "✅ Attendance Record"])

        # ---------- LIBRARY TAB ----------
        with tab_library:
            books = get_issued_books(student["student_id"])

            if not books:
                st.info("This student has no books currently issued.")
            else:
                st.caption(f"{len(books)} book(s) currently issued")
                for b in books:
                    status = get_book_status(b["due_date"])
                    remaining = days_remaining(b["due_date"])

                    if status == "overdue":
                        tag_class, tag_text = "tag-overdue", f"Overdue by {abs(remaining)} day(s)"
                    elif status == "due_soon":
                        tag_class, tag_text = "tag-soon", f"Due in {remaining} day(s)"
                    else:
                        tag_class, tag_text = "tag-ok", f"{remaining} day(s) left"

                    with st.container(border=True):
                        st.markdown(f'<p class="book-title">{b["title"]}</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="book-meta">{b["author"]}</p>', unsafe_allow_html=True)
                        st.markdown(
                            f'<p class="book-meta">Issued {b["issue_date"].strftime("%d %b %Y")} · '
                            f'Due {b["due_date"].strftime("%d %b %Y")}</p>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f'<span class="tag {tag_class}">{tag_text}</span>', unsafe_allow_html=True)

        # ---------- ATTENDANCE TAB ----------
        with tab_attendance:
            st.info(
                "Attendance records will appear here once the attendance module is connected "
                "(attendance %, dates present, and exam eligibility)."
            )