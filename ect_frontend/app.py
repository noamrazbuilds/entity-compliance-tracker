import streamlit as st
import streamlit.components.v1 as components

from ect_frontend.utils.api_client import client

st.set_page_config(
    page_title="Entity Compliance Tracker",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Shutdown flow: once triggered, replace the whole page and stop rendering.
# ---------------------------------------------------------------------------
if st.session_state.get("_shutdown_triggered"):
    # Take over the parent document with a static page before Streamlit's
    # websocket-reconnection UI can appear.
    _SHUTDOWN_HTML = """
    <script>
    (function() {
        var doc = window.parent.document;
        doc.open();
        doc.write(
            '<!DOCTYPE html>' +
            '<html><head><meta charset="utf-8">' +
            '<title>Entity Compliance Tracker — Shut Down</title>' +
            '<style>' +
            'body{margin:0;display:flex;align-items:center;justify-content:center;' +
            'height:100vh;background:#f8f9fa;font-family:-apple-system,' +
            'BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#333}' +
            '.card{text-align:center;padding:3rem;border-radius:12px;' +
            'background:#fff;box-shadow:0 2px 12px rgba(0,0,0,.08)}' +
            'h1{margin:0 0 .5rem;font-size:1.5rem}' +
            'p{margin:0;color:#666;font-size:1.05rem}' +
            '</style></head><body>' +
            '<div class="card">' +
            '<h1>App has been shut down.</h1>' +
            '<p>You can close this tab.</p>' +
            '</div></body></html>'
        );
        doc.close();
    })();
    </script>
    """
    components.html(_SHUTDOWN_HTML, height=0)
    st.stop()

# ---------------------------------------------------------------------------
# Normal app
# ---------------------------------------------------------------------------
st.title("Entity Compliance Tracker")
st.markdown(
    "Corporate entity registry with compliance calendar,"
    " org chart, and automated reminders."
)

st.sidebar.title("Navigation")
st.sidebar.info("Pages are available in the sidebar above.")

# Shutdown button in sidebar
st.sidebar.divider()
if st.sidebar.button("Shutdown App", type="secondary", use_container_width=True):
    try:
        client.post("/api/v1/shutdown")
    except Exception:
        pass  # Server may already be terminating
    st.session_state["_shutdown_triggered"] = True
    st.rerun()
