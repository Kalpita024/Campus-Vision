"""
components/extend_date.py
---------------------------
Reusable "Extend by N days" button for a single book. Call
render_extend_button(book, key_suffix=...) once per book from any page
that lists issued books (e.g. Issued_Books, Library_Card).

Depends on:
  - services/library_api.py -> extend_due_date()
  - utils/styles.py         -> banner()
"""

import streamlit as st
from services.library_api import extend_due_date
from utils.styles import banner


def render_extend_button(book: dict, key_suffix: str = "", extra_days: int = 7):
    """
    Renders an 'Extend by N days' button for a single book, and shows a
    success/failure banner right below it once clicked.

    Args:
        book: the book dict (needs 'book_id', 'title', 'renewed')
        key_suffix: unique suffix for the Streamlit widget key (use book_id)
        extra_days: how many days to extend the due date by
    """
    state_key = f"extend_result_{key_suffix}"

    clicked = st.button(
        f"Extend by {extra_days} days",
        key=f"extend_btn_{key_suffix}",
        disabled=book.get("renewed", False),
    )

    if clicked:
        result = extend_due_date(book["book_id"], extra_days=extra_days)
        st.session_state[state_key] = result
        st.rerun()

    result = st.session_state.get(state_key)
    if result:
        if result["success"]:
            banner(f"✅ {result['message']}", kind="ok")
        else:
            banner(f"❌ {result['message']}", kind="overdue")
