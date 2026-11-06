"""
pages/6_Attendance_History.py
-----------------------------
Student view: every attendance record (date, subject, present/absent)
with filters and a CSV download. "Marked at" and "Verified by" columns
appear automatically if the data includes them.
"""

import pandas as pd
import streamlit as st

from components.defaulter_alerts import (
    demo_data_notice,
    get_attendance_history,
    percentage,
    require_login,
)
from components.navbar import render_navbar
from utils.styles import inject_library_styles

st.set_page_config(page_title="Attendance History", page_icon="🗓️", layout="wide")

render_navbar("Attendance History")
inject_library_styles()

require_login("student")   # login screen in app.py sets logged_in / role / student_id
student_id = st.session_state["student_id"]

st.subheader("🗓️ Attendance History")

records = get_attendance_history(student_id)

if not records:
    st.info("No attendance records yet. They will appear here once attendance is taken.")
    st.stop()

df = pd.DataFrame(records)
df["date"] = pd.to_datetime(df["date"]).dt.date   # accepts date objects or "YYYY-MM-DD"
for optional in ("time", "method"):               # not every data source has these
    if optional not in df:
        df[optional] = "—"
df = df.sort_values(["date", "time"], ascending=False)

# ---- Filters ---------------------------------------------------------------
f1, f2, f3 = st.columns(3)

subject_choice = f1.selectbox("Subject", ["All subjects"] + sorted(df["subject"].unique()))
status_choice = f2.selectbox("Status", ["All", "Present", "Absent"])

min_day, max_day = df["date"].min(), df["date"].max()
picked = f3.date_input(
    "Date range", value=(min_day, max_day), min_value=min_day, max_value=max_day
)

filtered = df
if subject_choice != "All subjects":
    filtered = filtered[filtered["subject"] == subject_choice]
if status_choice != "All":
    filtered = filtered[filtered["status"] == status_choice]
# date_input returns a 1-item tuple while the user is still choosing the end date
if isinstance(picked, (tuple, list)) and len(picked) == 2:
    filtered = filtered[(filtered["date"] >= picked[0]) & (filtered["date"] <= picked[1])]

# ---- Summary of what is currently shown -------------------------------------
present = int((filtered["status"] == "Present").sum())
absent = int((filtered["status"] == "Absent").sum())

m1, m2, m3 = st.columns(3)
m1.metric("Present", present)
m2.metric("Absent", absent)
m3.metric("Attendance in this view", f"{percentage(present, present + absent):.1f}%")

# ---- Records table ----------------------------------------------------------
if filtered.empty:
    st.info("No records match these filters.")
else:
    view = filtered.rename(
        columns={
            "date": "Date",
            "subject": "Subject",
            "status": "Status",
            "time": "Marked at",
            "method": "Verified by",
        }
    )
    columns = ["Date", "Subject", "Status"]
    columns += [c for c in ("Marked at", "Verified by") if (view[c] != "—").any()]
    view = view[columns].copy()
    view["Status"] = view["Status"].map({"Present": "✅ Present", "Absent": "❌ Absent"})

    st.dataframe(view, hide_index=True)

    st.download_button(
        "⬇️ Download as CSV",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="attendance_history.csv",
        mime="text/csv",
    )

demo_data_notice("get_attendance_history")
