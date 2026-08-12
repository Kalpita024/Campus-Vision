"""
8_Extend_Date.py
------------------
Lets the student pick an issued book and extend (renew) its due date.
Uses st.session_state to remember which book was just extended so the
confirmation message survives the Streamlit re-run triggered by the button
click.

Depends on:
  - services/library_api.py  -> get_issued_books(), extend_due_date()
  - utils/styles.py          -> load_custom_css(), book_card(), banner(), section_title()
"""

import os
import sys

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if FRONTEND_DIR not in sys.path:
    sys.path.append(FRONTEND_DIR)

import streamlit as st
from services.library_api import get_issued_books, extend_due_date
from utils.styles import load_custom_css, section_title, banner, book_card

# ---------------------------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Extend Due Date", page_icon="📖")
load_custom_css()

student_id = st.session_state.get("student_id", "demo_student")

# Session-state keys this page owns:
#   "extend_confirmation" -> dict with the result of the last extend action,
#                             so the message stays visible after the re-run.
if "extend_confirmation" not in st.session_state:
    st.session_state["extend_confirmation"] = None

section_title("Extend / Renew a Book")

books = get_issued_books(student_id)

if not books:
    st.info("You have no issued books to extend right now.")
else:
    for b in books:
        book_card(
            title=b["title"],
            author=b["author"],
            meta_line=f"Due: {b['due_date'].strftime('%d %b %Y')}"
                      + (" · already renewed" if b["renewed"] else ""),
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            extend_clicked = st.button(
                "Extend by 7 days",
                key=f"extend_{b['book_id']}",
                disabled=b["renewed"],
            )

        if extend_clicked:
            result = extend_due_date(b["book_id"], extra_days=7)
            # Store result in session_state so it renders below, and persists
            # across the automatic re-run Streamlit does after a button click.
            st.session_state["extend_confirmation"] = {
                "book_id": b["book_id"],
                "title": b["title"],
                **result,
            }
            st.rerun()

# ---------------------------------------------------------------------------
# SHOW CONFIRMATION (if any extend action just happened)
# ---------------------------------------------------------------------------

confirmation = st.session_state.get("extend_confirmation")
if confirmation:
    st.divider()
    if confirmation["success"]:
        banner(f"✅ {confirmation['title']}: {confirmation['message']}", kind="ok")
    else:
        banner(f"❌ {confirmation['title']}: {confirmation['message']}", kind="overdue")

    if st.button("Dismiss"):
        st.session_state["extend_confirmation"] = None
        st.rerun()

st.caption(
    "Extension logic currently runs on stub data in `library_api.py` "
    "(one renewal allowed per book). Swap in real API calls once the "
    "backend endpoint is ready — the function signature won't need to change."
)
