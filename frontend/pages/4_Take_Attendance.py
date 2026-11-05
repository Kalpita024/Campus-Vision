"""
pages/4_Take_Attendance.py

Teacher-only page: take a photo (or upload class photos), recognise faces,
auto-tick the students who were found, let the teacher fix mistakes manually,
then save.
"""

import hashlib
from datetime import date

import cv2
import numpy as np
import streamlit as st

from services import attendance_api
from services.face_recognition import FaceRecognizer

st.set_page_config(page_title="Take Attendance", page_icon="📸", layout="wide")

# --------------------------- Role guard (from app.py) ----------------------- #
# app.py should set:  st.session_state["role"] = "Teacher"  or  "Student"
if st.session_state.get("role") != "Teacher":
    st.warning("Only teachers can take attendance. Please log in as a Teacher.")
    st.stop()

# Optional: if your components/navbar.py exposes a function, call it here, e.g.
# from components.navbar import render_navbar
# render_navbar()

st.title("📸 Take Attendance")


# ------------------------------- Cached model ------------------------------- #
@st.cache_resource
def load_recognizer(_version: int):
    return FaceRecognizer()


if "model_version" not in st.session_state:
    st.session_state.model_version = 0

with st.sidebar:
    if st.button("🔄 Reload face model"):
        st.session_state.model_version += 1
        st.rerun()

recognizer = load_recognizer(st.session_state.model_version)

if not recognizer.ready:
    st.error(
        "Face model not found. Run `python -m tools.enroll_faces`, enroll students "
        "and click **Train Model**, then press *Reload face model* in the sidebar."
    )
    st.stop()


# ------------------------------ Session details ----------------------------- #
classes = attendance_api.get_classes()
if not classes:
    st.warning("No students enrolled yet. Use the enrollment tool first.")
    st.stop()

c1, c2, c3 = st.columns(3)
class_name = c1.selectbox("Class", classes)
subject = c2.text_input("Subject", placeholder="e.g. Mathematics")
on_date = c3.date_input("Date", value=date.today())

students = attendance_api.get_students(class_name)
student_ids = [s["student_id"] for s in students]

# Reset state when the class changes
if st.session_state.get("active_class") != class_name:
    st.session_state.active_class = class_name
    st.session_state.processed_hashes = set()
    for sid in student_ids:
        st.session_state[f"chk_{sid}"] = False

st.session_state.setdefault("processed_hashes", set())
for sid in student_ids:
    st.session_state.setdefault(f"chk_{sid}", False)


# ------------------------------ Capture / upload ---------------------------- #
def process_image(data: bytes):
    """Run recognition on raw image bytes, tick detected students, return annotated image."""
    digest = hashlib.md5(data).hexdigest()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    results, annotated = recognizer.recognize(frame)

    # Only auto-tick once per image so manual un-ticks aren't overwritten on rerun
    if digest not in st.session_state.processed_hashes:
        st.session_state.processed_hashes.add(digest)
        for r in results:
            if r["student_id"] in student_ids:
                st.session_state[f"chk_{r['student_id']}"] = True
    return results, annotated


left, right = st.columns([3, 2])

with left:
    tab_cam, tab_upload = st.tabs(["📷 Camera", "🖼️ Upload class photo(s)"])
    annotated_images = []

    with tab_cam:
        shot = st.camera_input("Take a photo of the class")
        if shot is not None:
            results, annotated = process_image(shot.getvalue())
            annotated_images.append((annotated, results))

    with tab_upload:
        files = st.file_uploader(
            "Upload one or more photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True
        )
        for f in files or []:
            results, annotated = process_image(f.getvalue())
            annotated_images.append((annotated, results))

    for img, results in annotated_images:
        known = sum(1 for r in results if r["student_id"])
        st.image(img, caption=f"{len(results)} face(s) found, {known} recognised",
                 use_container_width=True)
        unknown = len(results) - known
        if unknown:
            st.info(f"{unknown} face(s) not recognised. Tick them manually in the list if needed.")

# ---------------------------------- Roster ---------------------------------- #
with right:
    st.subheader(f"Roster – {class_name}")

    b1, b2 = st.columns(2)
    if b1.button("Mark all present", use_container_width=True):
        for sid in student_ids:
            st.session_state[f"chk_{sid}"] = True
        st.rerun()
    if b2.button("Clear all", use_container_width=True):
        for sid in student_ids:
            st.session_state[f"chk_{sid}"] = False
        st.rerun()

    for s in students:
        st.checkbox(f"{s['name']}  ({s['student_id']})", key=f"chk_{s['student_id']}")

    present_count = sum(st.session_state[f"chk_{sid}"] for sid in student_ids)
    st.metric("Present", f"{present_count} / {len(student_ids)}")

    if st.button("💾 Save attendance", type="primary", use_container_width=True):
        if not subject.strip():
            st.error("Please enter the subject before saving.")
        else:
            records = {
                sid: attendance_api.PRESENT if st.session_state[f"chk_{sid}"] else attendance_api.ABSENT
                for sid in student_ids
            }
            attendance_api.mark_attendance(class_name, subject.strip(), records, on_date)
            st.success(
                f"Attendance saved for {class_name} – {subject} on {on_date.isoformat()} "
                f"({present_count} present, {len(student_ids) - present_count} absent)."
            )