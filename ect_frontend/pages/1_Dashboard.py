"""Dashboard page -- high-level metrics and upcoming filings."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from requests.exceptions import ConnectionError, RequestException

from ect_frontend.utils.api_client import client
from ect_frontend.utils.formatters import days_until, format_date, urgency_badge

st.set_page_config(page_title="Dashboard | ECT", layout="wide")
st.title("Dashboard")

# ---------------------------------------------------------------------------
# Fetch data
# ---------------------------------------------------------------------------
try:
    dashboard: dict = client.get("/api/dashboard")
except ConnectionError:
    st.error(
        "Could not connect to the API server at "
        f"{client.base_url}. Make sure the backend is running."
    )
    st.stop()
except RequestException as exc:
    st.error(f"API error: {exc}")
    st.stop()

# ---------------------------------------------------------------------------
# Top-level metrics
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_entities: int = dashboard.get("total_entities", 0)
upcoming_deadlines: int = dashboard.get("upcoming_deadlines_30d", 0)
overdue_items: int = dashboard.get("overdue_items", 0)
good_standing_pct: float = dashboard.get("good_standing_pct", 0.0)

col1.metric("Total Entities", total_entities)
col2.metric("Upcoming Deadlines (30d)", upcoming_deadlines)
col3.metric(
    "Overdue Items",
    overdue_items,
    delta=f"{overdue_items}" if overdue_items > 0 else None,
    delta_color="inverse",
)
col4.metric("Good Standing %", f"{good_standing_pct:.1f}%")

st.divider()

# ---------------------------------------------------------------------------
# Charts — entities by jurisdiction & type
# ---------------------------------------------------------------------------
chart_left, chart_right = st.columns(2)

by_jurisdiction: dict = dashboard.get("entities_by_jurisdiction", {})
if by_jurisdiction:
    with chart_left:
        st.subheader("Entities by Jurisdiction")
        df_jur = pd.DataFrame(
            list(by_jurisdiction.items()),
            columns=["Jurisdiction", "Count"],
        ).set_index("Jurisdiction")
        st.bar_chart(df_jur)

by_type: dict = dashboard.get("entities_by_type", {})
if by_type:
    with chart_right:
        st.subheader("Entities by Type")
        df_type = pd.DataFrame(
            list(by_type.items()),
            columns=["Type", "Count"],
        ).set_index("Type")
        st.bar_chart(df_type)

st.divider()

# ---------------------------------------------------------------------------
# Upcoming filings table (next 30 days)
# ---------------------------------------------------------------------------
st.subheader("Upcoming Filings (Next 30 Days)")

filings: list[dict] = dashboard.get("upcoming_filings", [])

if not filings:
    st.info("No upcoming filings in the next 30 days.")
else:
    header_html = """
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
    </thead>
    <tbody>
    """
    rows_html = ""
    for f in filings:
        due = f.get("due_date", "")
        status = f.get("status", "pending")
        remaining = days_until(due)
        badge = urgency_badge(due, status) if due else ""
        rows_html += f"""
        <tr style="border-bottom:1px solid #eee;">
            <td style="padding:8px;">{f.get('entity_name', '')}</td>
            <td style="padding:8px;">{f.get('filing_type', '')}</td>
            <td style="padding:8px;">{f.get('jurisdiction', '')}</td>
            <td style="padding:8px;">{format_date(due)}</td>
            <td style="padding:8px;">{remaining}</td>
            <td style="padding:8px;">{badge}</td>
        </tr>
        """
    table_html = header_html + rows_html + "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)
