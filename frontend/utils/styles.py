"""
styles.py
---------
Central place for custom CSS so every page in the app looks consistent.

Usage in any page file:

    from utils.styles import load_custom_css, banner, section_title

    load_custom_css()          # call once near the top of the page
    section_title("My Books")  # styled heading
    banner("2 books overdue", kind="overdue")
"""

import streamlit as st


def load_custom_css() -> None:
    """Inject the app-wide CSS. Call this once at the top of every page."""
    st.markdown(
        """
        <style>
        /* ---- General page polish ---- */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* ---- Card used for each issued book ---- */
        .book-card {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .book-card h4 {
            margin: 0 0 0.25rem 0;
        }
        .book-meta {
            color: #666666;
            font-size: 0.85rem;
        }

        /* ---- Reminder banners ---- */
        .cv-banner {
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
            font-weight: 500;
        }
        .cv-banner-overdue {
            background-color: #fde2e2;
            color: #9b1c1c;
            border: 1px solid #f5b5b5;
        }
        .cv-banner-upcoming {
            background-color: #fff4d6;
            color: #8a6100;
            border: 1px solid #f7dd8a;
        }
        .cv-banner-ok {
            background-color: #e3f6e6;
            color: #1e6b34;
            border: 1px solid #b6e3bd;
        }

        /* ---- Section titles ---- */
        .cv-section-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid #4a6cf7;
            padding-left: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    """Styled section heading, used instead of a plain st.header()."""
    st.markdown(f'<div class="cv-section-title">{text}</div>', unsafe_allow_html=True)


def banner(message: str, kind: str = "ok") -> None:
    """
    Render a colored banner.
    kind: "overdue" (red), "upcoming" (yellow), or "ok" (green).
    """
    css_class = {
        "overdue": "cv-banner-overdue",
        "upcoming": "cv-banner-upcoming",
        "ok": "cv-banner-ok",
    }.get(kind, "cv-banner-ok")

    st.markdown(f'<div class="cv-banner {css_class}">{message}</div>', unsafe_allow_html=True)


def book_card(title: str, author: str, meta_line: str) -> None:
    """Consistent card layout for displaying a single book."""
    st.markdown(
        f"""
        <div class="book-card">
            <h4>{title}</h4>
            <div class="book-meta">{author}</div>
            <div class="book-meta">{meta_line}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
