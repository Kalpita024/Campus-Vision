"""
pages/5_Attendance_Status.py
----------------------------
Student view: overall attendance %, exam-eligibility alert, and a
subject-wise breakdown with what to do next in each subject.
"""

import pandas as pd
import streamlit as st

from components.defaulter_alerts import (
    ATTENDANCE_THRESHOLD,
    classify,
    demo_data_notice,
    get_attendance_summary,
    next_step,
    percentage,
    require_login,
    show_defaulter_alert,
    status_badge,
)
from components.navbar import render_navbar
from utils.styles import inject_library_styles

st.set_page_config(page_title="Attendance Status", page_icon="📊", layout="wide")

render_navbar("Attendance Status")
inject_library_styles()

require_login("student")   # login screen in app.py sets logged_in / role / student_id
student_id = st.session_state["student_id"]

st.subheader("📊 Your Attendance Status")

subjects = get_attendance_summary(student_id)

if not subjects:
    st.info("No attendance has been recorded for you yet.")
    st.stop()

total_attended = sum(s["attended"] for s in subjects)
total_lectures = sum(s["total"] for s in subjects)
overall_pct = percentage(total_attended, total_lectures)
overall_status = classify(overall_pct)

# ---- Headline numbers ------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Overall attendance",
    f"{overall_pct:.1f}%",
    delta=f"{overall_pct - ATTENDANCE_THRESHOLD:+.1f}% vs {ATTENDANCE_THRESHOLD}% limit",
)
c2.metric("Lectures attended", total_attended)
c3.metric("Total lectures", total_lectures)
c4.metric("Exam eligibility", status_badge(overall_status))

# ---- Eligibility alert -----------------------------------------------------
show_defaulter_alert(subjects)

# ---- Subject-wise table ----------------------------------------------------
st.markdown("#### Subject-wise attendance")

table = pd.DataFrame(
    [
        {
            "Subject": s["subject"],
            "Attended": s["attended"],
            "Total": s["total"],
            "Attendance": percentage(s["attended"], s["total"]),
            "Status": status_badge(classify(percentage(s["attended"], s["total"]))),
            "What next": next_step(s["attended"], s["total"]),
        }
        for s in subjects
    ]
).sort_values("Attendance")

st.dataframe(
    table,
    hide_index=True,
    column_config={
        "Attendance": st.column_config.ProgressColumn(
            "Attendance", min_value=0, max_value=100, format="%.1f%%"
        ),
    },
)

st.caption(f"Minimum required for exam eligibility: {ATTENDANCE_THRESHOLD}%.")
demo_data_notice("get_attendance_summary")
