import streamlit as st

def render_navbar():
    # ---------- SIDEBAR STYLING (matches app.py theme) ----------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Jost:wght@400;500;600&display=swap');

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
            st.markdown(f"""
                <div class="nav-user-box">
                    <p class="nav-user-label">Logged in as</p>
                    <p class="nav-user-name">{st.session_state.student_name}</p>
                </div>
            """, unsafe_allow_html=True)

            st.page_link("app.py", label="🏠  Home")
            st.page_link("pages/1_Dashboard.py", label="📊  Dashboard")

            st.divider()

            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.student_name = ""
                st.session_state.student_id = ""
                st.rerun()
        else:
            st.info("Please log in to continue.")