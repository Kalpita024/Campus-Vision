"""
pages/7_Defaulters.py
---------------------
Teacher view: which students are below the attendance limit, how many
lectures each one still needs, with class/subject filters, search and a
CSV download.
"""

import pandas as pd
import streamlit as st

from components.defaulter_alerts import (
    ATTENDANCE_THRESHOLD,
    AT_RISK_BUFFER,
    classify,
    demo_data_notice,
    get_class_attendance,
    lectures_needed,
    percentage,
    require_login,
    show_class_alert,
    status_badge,
)
from components.navbar import render_navbar
from utils.styles import inject_library_styles

st.set_page_config(page_title="Defaulters", page_icon="🚨", layout="wide")

render_navbar("Defaulters")
inject_library_styles()

require_login("teacher")   # login screen in app.py sets logged_in / role

st.subheader("🚨 Attendance Defaulters")

rows = get_class_attendance()

if not rows:
    st.info("No attendance has been recorded yet. Take attendance first, then come back here.")
    st.stop()

df = pd.DataFrame(rows)
df["name"] = df["name"].fillna(df["student_id"]).astype(str)
if "class_name" not in df:
    df["class_name"] = None
has_classes = df["class_name"].notna().any()
df["class_name"] = df["class_name"].fillna("—")

# ---- Filters ---------------------------------------------------------------
cols = st.columns(4 if has_classes else 3)
threshold = cols[0].slider(
    "Minimum attendance (%)", min_value=50, max_value=95, value=ATTENDANCE_THRESHOLD, step=5
)
slot = 1
class_choice = "All classes"
if has_classes:
    class_choice = cols[slot].selectbox("Class", ["All classes"] + sorted(df["class_name"].unique()))
    slot += 1
subject_choice = cols[slot].selectbox("Subject", ["All subjects"] + sorted(df["subject"].unique()))
search = cols[slot + 1].text_input("Search by name or ID", placeholder="e.g. Riya or S006")

if class_choice != "All classes":
    df = df[df["class_name"] == class_choice]

# One row per student: either their total across subjects, or just the chosen subject
keys = ["student_id", "name", "class_name"]
if subject_choice == "All subjects":
    per_student = df.groupby(keys, as_index=False)[["attended", "total"]].sum()
else:
    per_student = df[df["subject"] == subject_choice][keys + ["attended", "total"]].copy()

per_student["pct"] = [percentage(a, t) for a, t in zip(per_student["attended"], per_student["total"])]
per_student["status"] = [classify(p, threshold) for p in per_student["pct"]]
per_student["needed"] = [
    lectures_needed(a, t, threshold) for a, t in zip(per_student["attended"], per_student["total"])
]

if search.strip():
    q = search.strip().lower()
    per_student = per_student[
        per_student["name"].str.lower().str.contains(q, regex=False)
        | per_student["student_id"].astype(str).str.lower().str.contains(q, regex=False)
    ]

defaulters = per_student[per_student["status"] == "defaulter"].sort_values("pct")
at_risk = per_student[per_student["status"] == "at_risk"]

# ---- Summary ---------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Students", len(per_student))
m2.metric("Defaulters", len(defaulters))
m3.metric("At risk", len(at_risk), help=f"Within {AT_RISK_BUFFER} points above the limit")
m4.metric("Class average", f"{per_student['pct'].mean():.1f}%" if len(per_student) else "—")

show_class_alert(len(defaulters), len(per_student), threshold)


def _display(frame: pd.DataFrame) -> pd.DataFrame:
    """Rename/format columns for showing and exporting."""
    out = pd.DataFrame(
        {
            "Student ID": frame["student_id"],
            "Name": frame["name"],
            "Class": frame["class_name"],
            "Attended": frame["attended"],
            "Total": frame["total"],
            "Attendance": frame["pct"],
            "Status": frame["status"].map(status_badge),
            "Lectures to attend in a row": frame["needed"].map(lambda n: "—" if not n else str(int(n))),
        }
    )
    return out if has_classes else out.drop(columns=["Class"])


progress_col = {
    "Attendance": st.column_config.ProgressColumn(
        "Attendance", min_value=0, max_value=100, format="%.1f%%"
    )
}

# ---- Defaulter list ----------------------------------------------------------
st.markdown(f"#### Below {threshold}% ({len(defaulters)})")
if defaulters.empty:
    st.success("No students below the limit with the current filters.")
else:
    shown = _display(defaulters)
    st.dataframe(shown, hide_index=True, column_config=progress_col)
    st.download_button(
        "⬇️ Download defaulter list (CSV)",
        data=shown.to_csv(index=False).encode("utf-8"),
        file_name="defaulters.csv",
        mime="text/csv",
    )

# ---- Everyone ---------------------------------------------------------------
with st.expander("See all students"):
    st.dataframe(
        _display(per_student.sort_values("pct")), hide_index=True, column_config=progress_col
    )

demo_data_notice("get_class_attendance")
