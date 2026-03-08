"""Formatting utilities for the Entity Compliance Tracker frontend."""

from __future__ import annotations

import datetime
from datetime import date


def _to_date(d: str | date | None) -> date | None:
    """Convert a string or date to a date object."""
    if d is None:
        return None
    if isinstance(d, datetime.datetime):
        return d.date()
    if isinstance(d, date):
        return d
    # Try common formats
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.datetime.strptime(d, fmt).date()
        except ValueError:
            continue
    return None


def urgency_color(due_date: date) -> str:
    """Return a hex color based on how close the due date is.

    - Overdue: red (#dc3545)
    - Within 7 days: orange (#fd7e14)
    - Within 14 days: yellow (#ffc107)
    - Otherwise: green (#28a745)
    """
    delta = (due_date - date.today()).days
    if delta < 0:
        return "#dc3545"
    if delta <= 7:
        return "#fd7e14"
    if delta <= 14:
        return "#ffc107"
    return "#28a745"


def urgency_badge(due_date: date, status: str) -> str:
    """Return an HTML badge with urgency color coding.

    If status is 'filed', always return a green 'Filed' badge.
    Otherwise, show days remaining with urgency coloring.
    """
    if status.lower() == "filed":
        return (
            '<span style="background-color:#28a745;color:#fff;'
            'padding:2px 8px;border-radius:10px;font-size:0.85em;">'
            "Filed</span>"
        )

    delta = days_until(due_date)
    color = urgency_color(due_date)

    if delta < 0:
        label = f"Overdue ({abs(delta)}d)"
    elif delta == 0:
        label = "Due Today"
    else:
        label = f"{delta}d remaining"

    return (
        f'<span style="background-color:{color};color:#fff;'
        f'padding:2px 8px;border-radius:10px;font-size:0.85em;">'
        f"{label}</span>"
    )


def format_date(d: str | date | None) -> str:
    """Format a date as 'Mar 4, 2026'. Returns '—' for None."""
    parsed = _to_date(d)
    if parsed is None:
        return "\u2014"
    return parsed.strftime("%b %-d, %Y")


def days_until(due_date: str | date) -> int:
    """Return the number of days until *due_date* (negative if overdue)."""
    parsed = _to_date(due_date)
    if parsed is None:
        return 0
    return (parsed - date.today()).days
