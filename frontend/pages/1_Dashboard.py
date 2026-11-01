import os
import streamlit as st
from components.navbar import render_navbar
from services.library_api import get_issued_books, get_due_reminders

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Dashboard - CampusVision",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

render_navbar("Dashboard")

# ---------- LOGIN GUARD ----------
if not st.session_state.get("logged_in", False):
    st.warning("Please log in first from the Home page.")
    st.stop()

role = st.session_state.get("role", "student")
is_teacher = role == "teacher"
FRONTEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

    .stat-label {
        font-family: 'Jost', sans-serif;
        color: #A69B85;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.2rem;
    }
    .stat-value {
        font-family: 'Cormorant Garamond', serif;
        color: #3B3226;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }

    div[data-testid="stAlert"] {
        border-radius: 2px;
        font-family: 'Jost', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)


def stat_card(label: str, value) -> None:
    """One small stat box in the theme."""
    with st.container(border=True):
        st.markdown(f'<p class="stat-label">{label}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="stat-value">{value}</p>', unsafe_allow_html=True)


def quick_links(links) -> None:
    """Show a link only if its page file exists."""
    for path, label in links:
        if os.path.exists(os.path.join(FRONTEND_DIR, path)):
            st.page_link(path, label=label)


# ---------- HERO HEADER ----------
subtitle = "Teacher Dashboard" if is_teacher else "Your Library Dashboard"
st.markdown(f"""
    <div class="hero">
        <h1>Welcome, {st.session_state.student_name}</h1>
        <p>{subtitle}</p>
    </div>
""", unsafe_allow_html=True)

# ======================================================================
# TEACHER VIEW
# ======================================================================
if is_teacher:
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("Classes Today", "—")
    with col2:
        stat_card("Present Today", "—")
    with col3:
        stat_card("Defaulters", "—")

    st.write("")

    with st.container(border=True):
        st.markdown('<p class="section-title">Quick Access</p>', unsafe_allow_html=True)
        quick_links([
            ("pages/4_Take_Attendance.py", "📷  Take Attendance"),
            ("pages/7_Defaulters.py", "⚠️  View Defaulters"),
            ("pages/8_Student_Record.py", "🔎  Look up a Student by Roll No."),
        ])
        st.info("These numbers will fill in automatically once the attendance pages are connected.")

# ======================================================================
# STUDENT VIEW
# ======================================================================
else:
    student_id = st.session_state.get("student_id", "")
    books = get_issued_books(student_id)
    reminders = get_due_reminders(student_id)

    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("Books Issued", len(books))
    with col2:
        stat_card("Due Soon", len(reminders["upcoming"]))
    with col3:
        stat_card("Overdue", len(reminders["overdue"]))

    st.write("")

    with st.container(border=True):
        st.markdown('<p class="section-title">Quick Access</p>', unsafe_allow_html=True)
        quick_links([
            ("pages/2_Library_Card.py", "📇  My Library Card"),
            ("pages/3_Issued_Books.py", "📚  My Issued Books"),
            ("pages/5_Attendance_Status.py", "✅  My Attendance"),
        ])
        if reminders["overdue"]:
            st.warning("You have overdue books. Open Issued Books to renew or return them.")
        elif reminders["upcoming"]:
            st.info("Some books are due soon. You can extend them from Issued Books.")