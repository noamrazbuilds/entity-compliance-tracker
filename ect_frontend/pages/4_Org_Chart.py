"""Streamlit page – Interactive Org Chart visualisation."""

from __future__ import annotations

import streamlit as st
from requests.exceptions import RequestException

from ect_frontend.components.org_chart import ENTITY_COLORS, render_org_chart
from ect_frontend.utils.api_client import client

st.set_page_config(page_title="Org Chart", page_icon="\U0001f3e2", layout="wide")

st.title("Organisation Chart")
st.caption("Interactive hierarchy of corporate entities and ownership relationships.")

# ---------------------------------------------------------------------------
# Sidebar – legend & controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.subheader("Controls")
    expand_all = st.button("Expand All", use_container_width=True)
    collapse_all = st.button("Collapse All", use_container_width=True)

    st.divider()
    st.subheader("Legend")
    _PRETTY = {
        "corporation": "Corporation",
        "llc": "LLC",
        "lp": "LP / LLP",
        "limited_company": "Limited Company",
        "nonprofit": "Nonprofit",
        "other": "Other / Portfolio",
    }
    for key, label in _PRETTY.items():
        colour = ENTITY_COLORS[key]
        st.markdown(
            f'<span style="display:inline-block;width:14px;height:14px;'
            f"border-radius:3px;background:{colour};vertical-align:middle;"
            f'margin-right:6px;"></span> {label}',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Helpers to recursively set expanded / collapsed state
# ---------------------------------------------------------------------------

def _set_expanded(node: dict, expanded: bool) -> dict:
    """Return a shallow-copy of *node* with children exposed or hidden.

    When *expanded* is True every ``_children`` key (D3 convention for
    hidden children) is moved back to ``children`` so the chart opens
    fully.  When False, all children below root are kept but the front-end
    will receive the data with an ``_collapsed`` flag the JS honours.

    Because the raw API data uses only ``children`` (no ``_children``),
    the simplest approach is to annotate each node with a flag that the
    JS template reads on initial render.
    """
    node = dict(node)  # shallow copy
    node["_default_collapsed"] = not expanded
    if node.get("children"):
        node["children"] = [_set_expanded(c, expanded) for c in node["children"]]
    return node


# ---------------------------------------------------------------------------
# Fetch data
# ---------------------------------------------------------------------------

try:
    tree_data = client.get("/api/relationships/org-tree")
except RequestException as exc:
    st.error(f"Failed to load org-tree data from the API: {exc}")
    st.stop()

# Normalise to a single root dict
if isinstance(tree_data, list):
    if not tree_data:
        tree_data = None
    else:
        tree_data = tree_data[0]

if not tree_data:
    st.info(
        "No organisational relationships have been created yet.\n\n"
        "Head over to the **Entities** page to add entities, then create "
        "ownership relationships to see the hierarchy here."
    )
    st.stop()

# Apply expand / collapse preference
if expand_all:
    tree_data = _set_expanded(tree_data, expanded=True)
elif collapse_all:
    tree_data = _set_expanded(tree_data, expanded=False)

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
render_org_chart(tree_data, height=700)
