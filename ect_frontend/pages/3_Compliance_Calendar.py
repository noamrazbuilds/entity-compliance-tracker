"""Compliance Calendar page -- list and calendar views of all filing deadlines."""

from __future__ import annotations

import calendar
from datetime import date

import streamlit as st
from requests.exceptions import ConnectionError, RequestException

from ect_frontend.utils.api_client import client
from ect_frontend.utils.formatters import (
    days_until,
    format_date,
    urgency_badge,
    urgency_color,
)

st.set_page_config(page_title="Compliance Calendar | ECT", layout="wide")
st.title("Compliance Calendar")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "cal_view" not in st.session_state:
    st.session_state.cal_view = "list"
if "cal_year" not in st.session_state:
    st.session_state.cal_year = date.today().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = date.today().month

# ---------------------------------------------------------------------------
# View toggle
# ---------------------------------------------------------------------------
view_col1, view_col2, _ = st.columns([1, 1, 6])
if view_col1.button("List View", key="cal_list_btn"):
    st.session_state.cal_view = "list"
    st.rerun()
if view_col2.button("Calendar View", key="cal_cal_btn"):
    st.session_state.cal_view = "calendar"
    st.rerun()

# ---------------------------------------------------------------------------
# Fetch data
# ---------------------------------------------------------------------------
try:
    upcoming: list[dict] = client.get("/api/filings/upcoming", params={"days": 365})
except (ConnectionError, RequestException):
    upcoming = []

try:
    overdue: list[dict] = client.get("/api/filings/overdue")
except (ConnectionError, RequestException):
    overdue = []

# Merge and deduplicate by id
seen_ids: set[int] = set()
all_filings: list[dict] = []
for f in overdue + upcoming:
    fid = f.get("id")
    if fid not in seen_ids:
        seen_ids.add(fid)
        all_filings.append(f)

# Sort by due_date
all_filings.sort(key=lambda f: f.get("due_date", "9999-99-99"))

if not all_filings:
    st.info("No filings found. Add filing deadlines from the Entity Registry page.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

all_entities = sorted({f.get("entity_name", "") for f in all_filings if f.get("entity_name")})
all_jurisdictions = sorted(
    {f.get("jurisdiction", "") for f in all_filings if f.get("jurisdiction")}
)
all_statuses = sorted({f.get("status", "") for f in all_filings if f.get("status")})

filter_entities: list[str] = st.sidebar.multiselect(
    "Entity", all_entities, key="cal_filt_ent"
)
filter_jurisdictions: list[str] = st.sidebar.multiselect(
    "Jurisdiction", all_jurisdictions, key="cal_filt_jur"
)
filter_statuses: list[str] = st.sidebar.multiselect(
    "Status", all_statuses, key="cal_filt_stat"
)
filter_date_range = st.sidebar.date_input(
    "Date Range",
    value=[],
    key="cal_filt_dates",
)


def _apply_filters(filings: list[dict]) -> list[dict]:
    """Apply sidebar filters to a list of filings."""
    filtered = filings
    if filter_entities:
        filtered = [f for f in filtered if f.get("entity_name") in filter_entities]
    if filter_jurisdictions:
        filtered = [f for f in filtered if f.get("jurisdiction") in filter_jurisdictions]
    if filter_statuses:
        filtered = [f for f in filtered if f.get("status") in filter_statuses]
    if filter_date_range and len(filter_date_range) == 2:
        start, end = filter_date_range
        filtered = [
            f
            for f in filtered
            if f.get("due_date") and str(start) <= f["due_date"][:10] <= str(end)
        ]
    return filtered


filtered_filings = _apply_filters(all_filings)

# =====================================================================
# LIST VIEW
# =====================================================================
if st.session_state.cal_view == "list":
    st.subheader("All Filing Deadlines")

    if not filtered_filings:
        st.info("No filings match the selected filters.")
        st.stop()

    table_html = """
    <table style="width:100%;border-collapse:collapse;">
    <thead>
    <tr style="text-align:left;border-bottom:2px solid #ddd;">
        <th style="padding:8px;">Entity</th>
        <th style="padding:8px;">Filing Type</th>
        <th style="padding:8px;">Jurisdiction</th>
        <th style="padding:8px;">Due Date</th>
        <th style="padding:8px;">Days Remaining</th>
        <th style="padding:8px;">Status</th>
    </tr>
    </thead><tbody>
    """
    for f in filtered_filings:
        due = f.get("due_date", "")
        status = f.get("status", "pending")
        remaining = days_until(due) if due else ""
        badge = urgency_badge(due, status) if due else status
        table_html += f"""
        <tr style="border-bottom:1px solid #eee;">
            <td style="padding:8px;">{f.get('entity_name', '')}</td>
            <td style="padding:8px;">{f.get('filing_type', '')}</td>
            <td style="padding:8px;">{f.get('jurisdiction', '')}</td>
            <td style="padding:8px;">{format_date(due)}</td>
            <td style="padding:8px;">{remaining}</td>
            <td style="padding:8px;">{badge}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

# =====================================================================
# CALENDAR VIEW
# =====================================================================
else:
    year = st.session_state.cal_year
    month = st.session_state.cal_month

    # Navigation
    nav1, nav2, nav3 = st.columns([1, 3, 1])
    if nav1.button("Previous", key="cal_prev"):
        if month == 1:
            st.session_state.cal_month = 12
            st.session_state.cal_year = year - 1
        else:
            st.session_state.cal_month = month - 1
        st.rerun()

    nav2.markdown(
        f"<h2 style='text-align:center;'>{calendar.month_name[month]} {year}</h2>",
        unsafe_allow_html=True,
    )

    if nav3.button("Next", key="cal_next"):
        if month == 12:
            st.session_state.cal_month = 1
            st.session_state.cal_year = year + 1
        else:
            st.session_state.cal_month = month + 1
        st.rerun()

    # Build a map: day -> list of filings
    filings_by_day: dict[int, list[dict]] = {}
    for f in filtered_filings:
        due = f.get("due_date", "")
        if not due:
            continue
        due_str = due[:10]  # "YYYY-MM-DD"
        try:
            parts = due_str.split("-")
            d_year, d_month, d_day = int(parts[0]), int(parts[1]), int(parts[2])
        except (ValueError, IndexError):
            continue
        if d_year == year and d_month == month:
            filings_by_day.setdefault(d_day, []).append(f)

    today = date.today()
    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    month_days = cal.monthdayscalendar(year, month)

    # Day-of-week headers
    day_headers = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Build HTML calendar
    html = """
    <style>
    .cal-table { width:100%; border-collapse:collapse; table-layout:fixed; }
    .cal-table th { padding:8px; text-align:center; background:#f0f2f6;
                    border:1px solid #ddd; font-weight:600; }
    .cal-table td { padding:6px; border:1px solid #ddd; vertical-align:top;
                    height:90px; font-size:0.85em; }
    .cal-today { background-color:#e8f0fe !important; }
    .cal-day-num { font-weight:600; margin-bottom:4px; }
    .cal-badge { display:inline-block; padding:1px 5px; border-radius:8px;
                 color:#fff; font-size:0.75em; margin:1px 0; max-width:100%;
                 overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    </style>
    <table class="cal-table">
    <thead><tr>
    """
    for dh in day_headers:
        html += f"<th>{dh}</th>"
    html += "</tr></thead><tbody>"

    for week in month_days:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += '<td style="background:#fafafa;"></td>'
                continue

            is_today = (year == today.year and month == today.month and day == today.day)
            td_class = ' class="cal-today"' if is_today else ""
            html += f"<td{td_class}>"
            html += f'<div class="cal-day-num">{day}</div>'

            day_filings = filings_by_day.get(day, [])
            for df in day_filings[:3]:  # Limit to 3 visible per cell
                due = df.get("due_date", "")
                status = df.get("status", "pending")
                if status.lower() == "filed":
                    color = "#28a745"
                elif due:
                    try:
                        d_parts = due[:10].split("-")
                        due_date_obj = date(int(d_parts[0]), int(d_parts[1]), int(d_parts[2]))
                        color = urgency_color(due_date_obj)
                    except (ValueError, IndexError):
                        color = "#6c757d"
                else:
                    color = "#6c757d"
                label = df.get("filing_type", "Filing")
                entity = df.get("entity_name", "")
                title_attr = f"{entity}: {label}"
                html += (
                    f'<div class="cal-badge" style="background:{color};" '
                    f'title="{title_attr}">{label}</div>'
                )
            if len(day_filings) > 3:
                extra = len(day_filings) - 3
                html += f'<div style="font-size:0.7em;color:#888;">+{extra} more</div>'

            html += "</td>"
        html += "</tr>"

    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)
