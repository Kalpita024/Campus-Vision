import streamlit as st
from components.navbar import render_navbar

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Dashboard - CampusVision",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

render_navbar()

# ---------- LOGIN GUARD ----------
if not st.session_state.get("logged_in", False):
    st.warning("Please log in first from the Home page.")
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

# ---------- HERO HEADER ----------
st.markdown(f"""
    <div class="hero">
        <h1>Welcome, {st.session_state.student_name}</h1>
        <p>Your Library Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# ---------- STATS ROW ----------
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown('<p class="stat-label">Books Issued</p>', unsafe_allow_html=True)
        st.markdown('<p class="stat-value">0</p>', unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown('<p class="stat-label">Due Soon</p>', unsafe_allow_html=True)
        st.markdown('<p class="stat-value">0</p>', unsafe_allow_html=True)

with col3:
    with st.container(border=True):
        st.markdown('<p class="stat-label">Overdue</p>', unsafe_allow_html=True)
        st.markdown('<p class="stat-value">0</p>', unsafe_allow_html=True)

st.write("")

# ---------- QUICK LINKS SECTION ----------
with st.container(border=True):
    st.markdown('<p class="section-title">Quick Access</p>', unsafe_allow_html=True)
    st.write("Your Library Card and Issued Books sections will appear here once those pages are built.")
    st.info("This dashboard will automatically update with real data once the library module is connected.")