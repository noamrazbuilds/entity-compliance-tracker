"""Settings page -- notification configuration and testing."""

from __future__ import annotations

import streamlit as st
from requests.exceptions import ConnectionError, RequestException

from ect_frontend.utils.api_client import client

st.set_page_config(page_title="Settings | ECT", layout="wide")
st.title("Settings")

# ---------------------------------------------------------------------------
# Helper: fetch entities for the override selector
# ---------------------------------------------------------------------------


@st.cache_data(ttl=60)
def _fetch_entities() -> list[dict]:
    try:
        return client.get("/api/entities/")
    except Exception:
        return []


# ---------------------------------------------------------------------------
# 1. Global Notification Defaults
# ---------------------------------------------------------------------------
st.header("Global Notification Defaults")

try:
    all_settings: list[dict] = client.get("/api/notifications/settings")
except ConnectionError:
    st.error(
        f"Could not connect to the API server at {client.base_url}. "
        "Make sure the backend is running."
    )
    st.stop()
except RequestException as exc:
    st.error(f"API error: {exc}")
    st.stop()

global_settings = [s for s in all_settings if s.get("entity_id") is None]

if global_settings:
    for gs in global_settings:
        col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
        col1.write(f"**Channel:** {gs['channel']}")
        col2.write(f"**Enabled:** {'Yes' if gs['enabled'] else 'No'}")
        col3.write(f"**Intervals:** {gs['reminder_days_before']} days")
        if col4.button("Delete", key=f"del_global_{gs['id']}"):
            try:
                client.delete(f"/api/notifications/settings/{gs['id']}")
                st.rerun()
            except RequestException as exc:
                st.error(f"Failed to delete: {exc}")
else:
    st.info("No global defaults configured. Add one below.")

st.subheader("Add / Update Global Default")
with st.form("global_default_form"):
    g_channel = st.selectbox("Channel", ["email", "slack", "both"], key="g_channel")
    g_intervals = st.text_input(
        "Reminder intervals (comma-separated days)", value="30,14,7", key="g_intervals"
    )
    g_recipients = st.text_input(
        "Recipients (comma-separated emails or webhook URL)", key="g_recipients"
    )
    g_enabled = st.checkbox("Enabled", value=True, key="g_enabled")
    g_submitted = st.form_submit_button("Save Global Default")

if g_submitted:
    payload = {
        "entity_id": None,
        "channel": g_channel,
        "reminder_days_before": g_intervals,
        "recipients": g_recipients or None,
        "enabled": g_enabled,
    }
    try:
        client.post("/api/notifications/settings", json=payload)
        st.success("Global default saved.")
        st.rerun()
    except RequestException as exc:
        st.error(f"Failed to save: {exc}")

st.divider()

# ---------------------------------------------------------------------------
# 2. Per-Entity Overrides
# ---------------------------------------------------------------------------
st.header("Per-Entity Overrides")

entity_settings = [s for s in all_settings if s.get("entity_id") is not None]

if entity_settings:
    for es in entity_settings:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        col1.write(f"**Entity ID:** {es['entity_id']}")
        col2.write(f"**Channel:** {es['channel']}")
        col3.write(f"**Intervals:** {es['reminder_days_before']}")
        col4.write(f"**Enabled:** {'Yes' if es['enabled'] else 'No'}")
        if col5.button("Delete", key=f"del_entity_{es['id']}"):
            try:
                client.delete(f"/api/notifications/settings/{es['id']}")
                st.rerun()
            except RequestException as exc:
                st.error(f"Failed to delete: {exc}")
else:
    st.info("No per-entity overrides configured.")

st.subheader("Add Per-Entity Override")

entities = _fetch_entities()
entity_options = {f"{e.get('name', 'Unknown')} (ID {e['id']})": e["id"] for e in entities}

if not entity_options:
    st.warning("No entities found. Create entities first.")
else:
    with st.form("entity_override_form"):
        selected_entity_label = st.selectbox(
            "Entity", list(entity_options.keys()), key="eo_entity"
        )
        eo_channel = st.selectbox(
            "Channel", ["email", "slack", "both"], key="eo_channel"
        )
        eo_intervals = st.text_input(
            "Reminder intervals (comma-separated days)",
            value="30,14,7",
            key="eo_intervals",
        )
        eo_recipients = st.text_input(
            "Recipients (comma-separated emails or webhook URL)",
            key="eo_recipients",
        )
        eo_enabled = st.checkbox("Enabled", value=True, key="eo_enabled")
        eo_submitted = st.form_submit_button("Save Override")

    if eo_submitted and selected_entity_label:
        payload = {
            "entity_id": entity_options[selected_entity_label],
            "channel": eo_channel,
            "reminder_days_before": eo_intervals,
            "recipients": eo_recipients or None,
            "enabled": eo_enabled,
        }
        try:
            client.post("/api/notifications/settings", json=payload)
            st.success("Per-entity override saved.")
            st.rerun()
        except RequestException as exc:
            st.error(f"Failed to save: {exc}")

st.divider()

# ---------------------------------------------------------------------------
# 3. Test Notification
# ---------------------------------------------------------------------------
st.header("Test Notification")

with st.form("test_notification_form"):
    t_channel = st.selectbox("Channel", ["email", "slack"], key="t_channel")
    t_recipient = st.text_input(
        "Recipient (email address or Slack webhook URL)", key="t_recipient"
    )
    t_submitted = st.form_submit_button("Send Test")

if t_submitted:
    if not t_recipient:
        st.warning("Please enter a recipient.")
    else:
        try:
            result = client.post(
                "/api/notifications/test",
                json={"channel": t_channel, "recipient": t_recipient},
            )
            if result.get("success"):
                st.success(result.get("message", "Test sent."))
            else:
                st.error(result.get("message", "Test failed."))
        except RequestException as exc:
            st.error(f"Error: {exc}")

st.divider()

# ---------------------------------------------------------------------------
# 4. Notification Log
# ---------------------------------------------------------------------------
st.header("Notification Log")

auto_refresh = st.checkbox("Auto-refresh (every 30s)", value=False, key="log_refresh")
if auto_refresh:
    st.empty()  # placeholder for auto-refresh via rerun
    import time
    # Streamlit will auto-rerun when the checkbox state changes;
    # use st.rerun with a timer for polling
    # We rely on streamlit's native fragment or manual refresh below.

try:
    logs: list[dict] = client.get("/api/notifications/log", params={"limit": 50})
except RequestException:
    logs = []

if logs:
    import pandas as pd

    df = pd.DataFrame(logs)
    display_cols = [
        "id",
        "filing_deadline_id",
        "channel",
        "reminder_days_before",
        "sent_at",
        "status",
        "error_message",
    ]
    existing = [c for c in display_cols if c in df.columns]
    st.dataframe(df[existing], use_container_width=True, hide_index=True)
else:
    st.info("No notification log entries yet.")

if auto_refresh:
    import time

    time.sleep(30)
    st.rerun()
