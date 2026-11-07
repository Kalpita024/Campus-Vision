"""
services/attendance_calc.py  -- PERSON 3
----------------------------------------
Attendance maths. Pure Python (no Flask, no database) so it is easy to test.
Same formulas as frontend/components/defaulter_alerts.py.
"""

import math

ATTENDANCE_THRESHOLD = 75   # minimum % needed for exam eligibility (assumed)
AT_RISK_BUFFER = 5          # within this many points above the limit = "at risk"


def percentage(attended, total):
    """Attendance % rounded to 1 decimal. 0 lectures -> 0.0."""
    if not total:
        return 0.0
    return round(100.0 * attended / total, 1)


def classify(pct, threshold=ATTENDANCE_THRESHOLD):
    """'defaulter' (below limit), 'at_risk' (just above) or 'eligible'."""
    if pct < threshold:
        return "defaulter"
    if pct < threshold + AT_RISK_BUFFER:
        return "at_risk"
    return "eligible"


def lectures_needed(attended, total, threshold=ATTENDANCE_THRESHOLD):
    """How many lectures in a row must be attended to reach the limit."""
    if total == 0 or 100 * attended >= threshold * total:
        return 0
    if threshold >= 100:
        return 0   # impossible to recover to 100% once a lecture is missed
    return math.ceil((threshold * total - 100 * attended) / (100 - threshold))


def lectures_can_miss(attended, total, threshold=ATTENDANCE_THRESHOLD):
    """How many more lectures can be missed while staying at/above the limit."""
    if total == 0 or 100 * attended < threshold * total:
        return 0
    return math.floor(100 * attended / threshold - total)


def summarise(attended, total, threshold=ATTENDANCE_THRESHOLD):
    """Everything the frontend needs for one (student, subject) or one student."""
    pct = percentage(attended, total)
    return {
        "attended": attended,
        "total": total,
        "percentage": pct,
        "status": classify(pct, threshold),
        "lectures_needed": lectures_needed(attended, total, threshold),
        "lectures_can_miss": lectures_can_miss(attended, total, threshold),
    }
