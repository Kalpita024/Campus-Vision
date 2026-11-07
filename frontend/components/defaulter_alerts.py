"""
components/defaulter_alerts.py
------------------------------
Shared pieces for the three Person 3 attendance pages
(5_Attendance_Status, 6_Attendance_History, 7_Defaulters):

  1. Attendance maths   -> percentage(), classify(), lectures_needed(), ...
  2. Alert banners      -> show_defaulter_alert() (student), show_class_alert() (teacher)
  3. Login guard        -> require_login()
  4. Data access        -> get_attendance_summary(), get_attendance_history(),
                           get_class_attendance()

DATA ACCESS - where the numbers come from
-----------------------------------------
Each get_* function looks for data in this order:

  a) a function with the SAME NAME in services/attendance_api.py (if the team
     adds one later), else
  b) services.attendance_api.get_attendance(...) - the function Person 2
     already wrote. Present/Absent rows are counted here, so percentages are
     always calculated from the real attendance table, else
  c) built-in demo data (the pages then show a small "demo data" note).

Return shapes (for option a):
    get_attendance_summary(student_id) -> [ {"subject", "attended", "total"}, ... ]
    get_attendance_history(student_id) -> [ {"date", "subject", "status"}, ... ]
        (optional extra keys: "time", "method")
    get_class_attendance()             -> [ {"student_id", "name", "class_name",
                                             "subject", "attended", "total"}, ... ]
"""

import html
import math
import random
from datetime import date, timedelta

import streamlit as st

# ---------------------------------------------------------------------------
# RULES - change here and every page follows
# ---------------------------------------------------------------------------

ATTENDANCE_THRESHOLD = 75   # minimum % for exam eligibility
AT_RISK_BUFFER = 5          # within this many points above the limit = "at risk"

PRESENT = "Present"         # same value attendance_api.py stores

STATUS_BADGES = {
    "eligible": "🟢 Eligible",
    "at_risk": "🟡 At risk",
    "defaulter": "🔴 Defaulter",
}


# ---------------------------------------------------------------------------
# 1. ATTENDANCE MATHS
# ---------------------------------------------------------------------------

def percentage(attended: int, total: int) -> float:
    """Attendance % rounded to 1 decimal; 0.0 when no lectures have happened."""
    return round(100 * attended / total, 1) if total else 0.0


def classify(pct: float, threshold: int = ATTENDANCE_THRESHOLD) -> str:
    """Return 'defaulter', 'at_risk' or 'eligible' for a percentage."""
    if pct < threshold:
        return "defaulter"
    if pct < threshold + AT_RISK_BUFFER:
        return "at_risk"
    return "eligible"


def status_badge(status: str) -> str:
    return STATUS_BADGES.get(status, status)


def lectures_needed(attended: int, total: int, threshold: int = ATTENDANCE_THRESHOLD):
    """
    How many lectures in a row the student must attend to reach `threshold`.
    0 if already there; None if it can never be reached (threshold >= 100).
    """
    if total == 0 or 100 * attended >= threshold * total:
        return 0
    if threshold >= 100:
        return None
    return math.ceil((threshold * total - 100 * attended) / (100 - threshold))


def lectures_can_miss(attended: int, total: int, threshold: int = ATTENDANCE_THRESHOLD) -> int:
    """How many more lectures can be missed while staying at/above `threshold`."""
    if threshold <= 0:
        return 0
    return max(0, math.floor(100 * attended / threshold - total))


def next_step(attended: int, total: int, threshold: int = ATTENDANCE_THRESHOLD) -> str:
    """One short sentence telling the student what to do next."""
    if 100 * attended < threshold * total:
        need = lectures_needed(attended, total, threshold)
        return f"Attend next {need} in a row" if need else "—"
    can_miss = lectures_can_miss(attended, total, threshold)
    return f"Can miss {can_miss} more" if can_miss else "Don't miss any more"


# ---------------------------------------------------------------------------
# 2. ALERT BANNERS (self-contained styling, no dependency on utils/styles.py)
# ---------------------------------------------------------------------------

_ALERT_CSS = (
    "<style>"
    ".cv-alert{border-radius:10px;padding:.8rem 1rem;margin:.4rem 0 .9rem 0;"
    "border:1px solid;line-height:1.5;}"
    ".cv-alert-title{font-weight:700;margin-bottom:.15rem;}"
    ".cv-alert-defaulter{background:#fde2e2;color:#9b1c1c;border-color:#f5b5b5;}"
    ".cv-alert-at_risk{background:#fff4d6;color:#8a6100;border-color:#f7dd8a;}"
    ".cv-alert-eligible{background:#e3f6e6;color:#1e6b34;border-color:#b6e3bd;}"
    "</style>"
)


def _render_alert(kind: str, title: str, body_html: str) -> None:
    # Kept on ONE line on purpose: Streamlit's markdown treats indented or
    # blank-line-separated HTML as a code block.
    st.markdown(
        f'{_ALERT_CSS}<div class="cv-alert cv-alert-{kind}">'
        f'<div class="cv-alert-title">{title}</div>{body_html}</div>',
        unsafe_allow_html=True,
    )


def show_defaulter_alert(subjects: list, threshold: int = ATTENDANCE_THRESHOLD):
    """
    Student-facing banner for the student's overall attendance, plus a line
    naming any subject that is individually below the limit.

    Returns (overall_percentage, status) so the page can reuse them.
    """
    attended = sum(s["attended"] for s in subjects)
    total = sum(s["total"] for s in subjects)
    pct = percentage(attended, total)
    status = classify(pct, threshold)

    if status == "defaulter":
        title = "⚠️ Attendance shortage"
        body = (
            f"Your overall attendance is <b>{pct:.1f}%</b>, below the "
            f"<b>{threshold}%</b> needed for exam eligibility."
        )
        need = lectures_needed(attended, total, threshold)
        if need:
            body += f" Attend the next <b>{need}</b> lectures in a row to get back to {threshold}%."
    elif status == "at_risk":
        title = "🟡 Close to the limit"
        can_miss = lectures_can_miss(attended, total, threshold)
        body = (
            f"Your overall attendance is <b>{pct:.1f}%</b> - only just above the "
            f"<b>{threshold}%</b> limit. You can miss at most <b>{can_miss}</b> more lectures."
        )
    else:
        title = "✅ You're eligible for exams"
        can_miss = lectures_can_miss(attended, total, threshold)
        body = (
            f"Your overall attendance is <b>{pct:.1f}%</b> (limit {threshold}%). "
            f"You can still miss <b>{can_miss}</b> lectures and stay eligible."
        )

    low = [
        f"{html.escape(str(s['subject']))} ({percentage(s['attended'], s['total']):.1f}%)"
        for s in subjects
        if classify(percentage(s["attended"], s["total"]), threshold) == "defaulter"
    ]
    if low:
        body += f"<br>Subjects below {threshold}%: {', '.join(low)}."

    _render_alert(status, title, body)
    return pct, status


def show_class_alert(defaulter_count: int, total_students: int,
                     threshold: int = ATTENDANCE_THRESHOLD) -> None:
    """Teacher-facing banner summarising how many students are below the limit."""
    if total_students == 0:
        return
    if defaulter_count:
        _render_alert(
            "defaulter",
            "⚠️ Attendance shortage in class",
            f"<b>{defaulter_count}</b> of <b>{total_students}</b> students are below "
            f"<b>{threshold}%</b> and are not eligible for exams right now.",
        )
    else:
        _render_alert(
            "eligible",
            "✅ No defaulters",
            f"All <b>{total_students}</b> students are at or above <b>{threshold}%</b>.",
        )


# ---------------------------------------------------------------------------
# 3. LOGIN GUARD
# ---------------------------------------------------------------------------

def require_login(role: str = None) -> None:
    """
    Stop the page with a friendly message unless the user is logged in
    (and, if `role` is given, has that role: "student" or "teacher").
    Uses the session keys set by the login screen in app.py:
    logged_in, role, student_id.
    """
    if not st.session_state.get("logged_in", False):
        st.info("Please log in from the Home page to see this page.")
        st.stop()
    if role and str(st.session_state.get("role", "")).strip().lower() != role:
        st.warning(f"This page is only available to {role}s.")
        st.stop()


# ---------------------------------------------------------------------------
# 4. DATA ACCESS  (team's attendance_api if available, demo data otherwise)
# ---------------------------------------------------------------------------

def _api_fn(name: str):
    """Return services.attendance_api.<name> if it exists, else None."""
    try:
        from services import attendance_api
    except ImportError:
        return None
    fn = getattr(attendance_api, name, None)
    return fn if callable(fn) else None


def _api_rows(**filters):
    """Rows from attendance_api.get_attendance(...), or None if it isn't available."""
    fn = _api_fn("get_attendance")
    return fn(**filters) if fn else None


def demo_data_notice(function_name: str) -> None:
    """Show a small note when the page is running on built-in demo data."""
    if _api_fn(function_name) is None and _api_fn("get_attendance") is None:
        st.caption(
            "ℹ️ Showing demo data - the attendance API isn't connected yet. "
            "This page switches to real data automatically once it is."
        )


def _count_by_subject(rows: list) -> list:
    """[{'subject', 'attended', 'total'}] from raw attendance rows (one row = one lecture)."""
    counts = {}
    for r in rows:
        entry = counts.setdefault(r["subject"], [0, 0])
        entry[1] += 1
        if r["status"] == PRESENT:
            entry[0] += 1
    return [
        {"subject": subject, "attended": a, "total": t}
        for subject, (a, t) in sorted(counts.items())
    ]


def get_attendance_summary(student_id: str) -> list:
    fn = _api_fn("get_attendance_summary")
    if fn:
        return fn(student_id)
    rows = _api_rows(student_id=student_id)
    if rows is not None:
        return _count_by_subject(rows)
    return _demo_subject_rows(_demo_index(student_id))


def get_attendance_history(student_id: str) -> list:
    fn = _api_fn("get_attendance_history")
    if fn:
        return fn(student_id)
    rows = _api_rows(student_id=student_id)
    if rows is not None:
        return [
            {"date": r["date"], "subject": r["subject"], "status": r["status"]}
            for r in rows
        ]
    return _demo_history(_demo_index(student_id))


def get_class_attendance() -> list:
    fn = _api_fn("get_class_attendance")
    if fn:
        return fn()
    rows = _api_rows()
    if rows is not None:
        grouped = {}
        for r in rows:
            entry = grouped.setdefault(
                (r["student_id"], r["subject"]),
                {
                    "student_id": r["student_id"],
                    "name": r.get("name") or r["student_id"],
                    "class_name": r.get("class_name"),
                    "subject": r["subject"],
                    "attended": 0,
                    "total": 0,
                },
            )
            entry["total"] += 1
            if r["status"] == PRESENT:
                entry["attended"] += 1
        return list(grouped.values())
    result = []
    for idx, (sid, name, class_name) in enumerate(_DEMO_STUDENTS):
        for r in _demo_subject_rows(idx):
            result.append({"student_id": sid, "name": name, "class_name": class_name, **r})
    return result


# ---------------------------------------------------------------------------
# DEMO DATA (delete this block once real attendance data is flowing)
# ---------------------------------------------------------------------------

_DEMO_SUBJECTS = [
    ("Machine Learning", 32),
    ("Database Systems", 30),
    ("Computer Networks", 28),
    ("Operating Systems", 30),
    ("Software Engineering", 26),
]

_DEMO_STUDENTS = [
    ("S001", "Aarohi Patil", "Class A"),
    ("S002", "Diya Menon", "Class A"),
    ("S003", "Isha Kulkarni", "Class A"),
    ("S004", "Meera Joshi", "Class A"),
    ("S005", "Naina Shah", "Class A"),
    ("S006", "Riya Deshmukh", "Class A"),
    ("S007", "Sana Khan", "Class B"),
    ("S008", "Tanvi Pawar", "Class B"),
    ("S009", "Utkarsha More", "Class B"),
    ("S010", "Vaishnavi Rane", "Class B"),
    ("S011", "Yashika Naik", "Class B"),
    ("S012", "Zoya Sheikh", "Class B"),
]

# How often each demo student attends (index matches _DEMO_STUDENTS)
_DEMO_RATES = [0.95, 0.90, 0.88, 0.82, 0.74, 0.72, 0.68, 0.92, 0.85, 0.60, 0.97, 0.80]


def _demo_index(student_id: str) -> int:
    """Map a student id to a demo student; unknown ids get S006 (a defaulter) so the alert is visible."""
    for i, (sid, _, _) in enumerate(_DEMO_STUDENTS):
        if sid == student_id:
            return i
    return 5


def _demo_subject_rows(idx: int) -> list:
    rng = random.Random(1000 + idx)
    rows = []
    for subject, total in _DEMO_SUBJECTS:
        rate = min(1.0, max(0.0, _DEMO_RATES[idx] + rng.uniform(-0.08, 0.08)))
        rows.append({"subject": subject, "attended": round(total * rate), "total": total})
    return rows


def _demo_history(idx: int) -> list:
    rng = random.Random(2000 + idx)
    records, day, weekdays, n = [], date.today(), 0, 0
    while weekdays < 28:
        day -= timedelta(days=1)
        if day.weekday() >= 5:  # skip Sat/Sun
            continue
        weekdays += 1
        for hour in (9, 11):
            subject = _DEMO_SUBJECTS[n % len(_DEMO_SUBJECTS)][0]
            n += 1
            present = rng.random() < _DEMO_RATES[idx]
            records.append({
                "date": day,
                "subject": subject,
                "status": "Present" if present else "Absent",
                "time": f"{hour:02d}:{rng.randint(2, 20):02d}" if present else "—",
                "method": "Face + GPS" if present else "—",
            })
    return records
