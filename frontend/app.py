import streamlit as st
from components.navbar import render_navbar

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="CampusVision",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

render_navbar()

# ---------- CUSTOM STYLING ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Jost', sans-serif;
    }

    /* Overall background - warm beige */
    .stApp {
        background: #F5F1EA;
    }

    .block-container {
        padding-top: 2.5rem;
    }

    /* Header banner */
    .hero {
        background: #FFFFFF;
        padding: 2.6rem 1.5rem 2rem 1.5rem;
        border-radius: 4px;
        text-align: center;
        border: 1px solid #E4DCCB;
        border-bottom: 3px solid #A88B5A;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-family: 'Cormorant Garamond', serif;
        color: #3B3226;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 1px;
    }
    .hero p {
        font-family: 'Jost', sans-serif;
        color: #8A7B60;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* Login/content card */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border-radius: 4px;
        border: 1px solid #E4DCCB !important;
    }

    .card-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: #3B3226;
        margin-bottom: 0.2rem;
    }
    .card-caption {
        font-family: 'Jost', sans-serif;
        color: #A69B85;
        font-size: 0.88rem;
        margin-bottom: 1.3rem;
        letter-spacing: 0.3px;
    }

    /* Inputs */
    div[data-testid="stTextInput"] input {
        border-radius: 2px;
        border: 1px solid #D8CDB8;
        background-color: #FBF9F5;
        padding: 0.65rem 0.9rem;
        font-family: 'Jost', sans-serif;
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
        font-family: 'Jost', sans-serif;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background: #3B3226;
        color: #F5F1EA;
        border-radius: 2px;
        padding: 0.65rem 0;
        font-weight: 500;
        font-size: 0.95rem;
        font-family: 'Jost', sans-serif;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border: none;
        transition: background 0.2s ease;
    }
    .stButton>button:hover {
        background: #A88B5A;
        color: #FFFFFF;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #FBF9F5;
        border-radius: 2px;
        padding: 0.9rem;
        border: 1px solid #E4DCCB;
    }
    div[data-testid="stMetricLabel"] {
        color: #A69B85;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.75rem;
    }
    div[data-testid="stMetricValue"] {
        color: #3B3226;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.8rem;
    }

    /* Success / info boxes */
    div[data-testid="stAlert"] {
        border-radius: 2px;
        font-family: 'Jost', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""

# ---------- HERO HEADER ----------
st.markdown("""
    <div class="hero">
        <h1>CampusVision</h1>
        <p>Smart Campus Management System</p>
    </div>
""", unsafe_allow_html=True)

# ---------- LOGIN VIEW ----------
if not st.session_state.logged_in:

    with st.container(border=True):
        st.markdown('<p class="card-title">Student Login</p>', unsafe_allow_html=True)
        st.markdown('<p class="card-caption">Enter your details to access the library portal</p>', unsafe_allow_html=True)

        name = st.text_input("Full Name", placeholder="e.g. Your name")
        student_id = st.text_input("Student ID", placeholder="e.g. UMIT2026045")

        login_clicked = st.button("Login")

        if login_clicked:
            if name.strip() and student_id.strip():
                st.session_state.logged_in = True
                st.session_state.student_name = name.strip()
                st.session_state.student_id = student_id.strip()
                st.rerun()
            else:
                st.error("Please enter both your name and Student ID.")

# ---------- LOGGED-IN VIEW ----------
else:
    with st.container(border=True):
        st.markdown(f'<p class="card-title">Welcome back, {st.session_state.student_name}</p>', unsafe_allow_html=True)
        st.markdown('<p class="card-caption">Here\'s your account overview</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Student ID", st.session_state.student_id)
        with col2:
            st.metric("Status", "Active")

        st.divider()
        st.info("Use the sidebar to navigate to your **Dashboard**, **Library Card**, and **Issued Books**.")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.student_name = ""
            st.session_state.student_id = ""
            st.rerun()