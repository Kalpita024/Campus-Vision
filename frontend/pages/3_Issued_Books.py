import streamlit as st
from components.navbar import render_navbar
from components.due_reminders import show_due_reminders
from components.extend_date import render_extend_button
from services.library_api import get_issued_books, get_book_status, days_remaining
from utils.styles import inject_library_styles

st.set_page_config(page_title="Issued Books", page_icon="📚", layout="wide")

render_navbar("Issued Books")
inject_library_styles()

st.subheader("📚 Your Issued Books")

books = get_issued_books()

if not books:
    st.info("You have no books issued right now. Visit the library to borrow one!")
else:
    # Reminder banners at the top — overdue / due-soon books surface first
    show_due_reminders(books)

    st.divider()

    for book in books:
        status = get_book_status(book["due_date"])
        remaining = days_remaining(book["due_date"])
        status_label = {
            "ok": "On track",
            "due_soon": "Due soon",
            "overdue": "Overdue",
        }[status]

        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            st.markdown(f"**{book['title']}**")
            st.caption(f"by {book['author']} · ISBN {book['isbn']}")

        with col2:
            st.markdown(
                f"Due: **{book['due_date'].strftime('%d %b %Y')}**  \n"
                f"<span class='status-badge status-{status}'>{status_label} "
                f"({remaining:+d} days)</span>",
                unsafe_allow_html=True,
            )

        with col3:
            render_extend_button(book, key_suffix=book["book_id"])

        st.divider()