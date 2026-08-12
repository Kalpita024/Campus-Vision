import streamlit as st
from components.navbar import render_navbar
from services.library_api import get_student_profile, get_issued_books
from utils.styles import inject_library_styles

st.set_page_config(page_title="Library Card", page_icon="📇", layout="centered")

render_navbar("Library Card")
inject_library_styles()

student = get_student_profile()
issued_count = len(get_issued_books(student["student_id"]))

st.markdown(
    f"""
    <div class="library-card">
        <div class="library-card-header">
            <div>
                <div style="font-size:1.15rem; font-weight:700;">{student['name']}</div>
                <div style="opacity:0.75; font-size:0.85rem;">{student['roll_no']}</div>
            </div>
            <div class="library-card-avatar">{student['photo_initials']}</div>
        </div>
        <div class="library-card-row"><span>Department</span><span>{student['department']}</span></div>
        <div class="library-card-row"><span>Year</span><span>{student['year']}</span></div>
        <div class="library-card-row"><span>Student ID</span><span>{student['student_id']}</span></div>
        <div class="library-card-row"><span>Email</span><span>{student['email']}</span></div>
        <div class="library-card-row"><span>Phone</span><span>{student['phone']}</span></div>
        <div class="library-card-row">
            <span>Membership valid till</span>
            <span>{student['membership_valid_till'].strftime('%d %b %Y')}</span>
        </div>
        <div class="library-card-row" style="border-bottom:none;">
            <span>Books currently issued</span><span>{issued_count}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("This is a digital representation of your library membership card. Show this at the counter if needed.")