import os
import streamlit as st

# frontend/ folder (this file lives in frontend/components/)
FRONTEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (page path, label). A link only shows if the file exists, so pages
# your teammates haven't pushed yet won't crash the app.
STUDENT_LINKS = [
    ("app.py", "🏠  Home"),
    ("pages/1_Dashboard.py", "📊  Dashboard"),
    ("pages/2_Library_Card.py", "📇  Library Card"),
    ("pages/3_Issued_Books.py", "📚  Issued Books"),
    ("pages/5_Attendance_Status.py", "✅  Attendance"),
    ("pages/6_Attendance_History.py", "🗓  Attendance History"),
]

TEACHER_LINKS = [
    ("app.py", "🏠  Home"),
    ("pages/1_Dashboard.py", "📊  Dashboard"),
    ("pages/4_Take_Attendance.py", "📷  Take Attendance"),
    ("pages/7_Defaulters.py", "⚠️  Defaulters"),
    ("pages/8_Student_Record.py", "🔎  Student Record"),
]


def render_navbar(current_page: str = "") -> None:
    # ---------- SIDEBAR STYLING (matches app.py theme) ----------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Jost:wght@400;500;600&display=swap');

        /* Hide Streamlit's automatic page list so each role
           only sees its own links */
        div[data-testid="stSidebarNav"] {
            display: none;
        }

        section[data-testid="stSidebar"] {
            background-color: #FBF9F5;
            border-right: 1px solid #E4DCCB;
        }

        .nav-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: #3B3226;
            margin-bottom: 0;
        }
        .nav-subtitle {
            font-family: 'Jost', sans-serif;
            color: #A69B85;
            font-size: 0.78rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 0;
            margin-bottom: 1.2rem;
        }
        .nav-user-box {
            background: #F5F1EA;
            border: 1px solid #E4DCCB;
            border-radius: 4px;
            padding: 0.7rem 0.9rem;
            margin-bottom: 1rem;
        }
        .nav-user-label {
            font-family: 'Jost', sans-serif;
            color: #A69B85;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 0;
        }
        .nav-user-name {
            font-family: 'Cormorant Garamond', serif;
            color: #3B3226;
            font-size: 1.15rem;
            font-weight: 700;
            margin: 0;
        }

        section[data-testid="stSidebar"] .stButton>button {
            width: 100%;
            background: #3B3226;
            color: #F5F1EA;
            border-radius: 2px;
            padding: 0.5rem 0;
            font-weight: 500;
            font-size: 0.85rem;
            font-family: 'Jost', sans-serif;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            border: none;
        }
        section[data-testid="stSidebar"] .stButton>button:hover {
            background: #A88B5A;
            color: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<p class="nav-title">📚 CampusVision</p>', unsafe_allow_html=True)
        st.markdown('<p class="nav-subtitle">Smart Campus System</p>', unsafe_allow_html=True)

        if st.session_state.get("logged_in", False):
            role = st.session_state.get("role", "student")
            name = st.session_state.get("student_name", "")

            st.markdown(f"""
                <div class="nav-user-box">
                    <p class="nav-user-label">Logged in as · {role.title()}</p>
                    <p class="nav-user-name">{name}</p>
                </div>
            """, unsafe_allow_html=True)

            links = TEACHER_LINKS if role == "teacher" else STUDENT_LINKS
            for path, label in links:
                if os.path.exists(os.path.join(FRONTEND_DIR, path)):
                    st.page_link(path, label=label)

            st.divider()

            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.student_name = ""
                st.session_state.student_id = ""
                st.session_state.role = ""
                st.rerun()
        else:
            st.info("Please log in to continue.")