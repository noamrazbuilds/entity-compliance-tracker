"""Entity Registry page -- full CRUD for entities and related records."""

from __future__ import annotations

import streamlit as st
from requests.exceptions import ConnectionError, RequestException

from ect_frontend.utils.api_client import client
from ect_frontend.utils.formatters import (
    format_date,
    urgency_badge,
)

st.set_page_config(page_title="Entity Registry | ECT", layout="wide")
st.title("Entity Registry")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ENTITY_TYPES: list[str] = [
    "corporation",
    "llc",
    "lp",
    "llp",
    "limited_company",
    "sole_proprietorship",
    "partnership",
    "nonprofit",
    "trust",
    "other",
]

# ---------------------------------------------------------------------------
# Session-state defaults
# ---------------------------------------------------------------------------
if "er_view" not in st.session_state:
    st.session_state.er_view = "list"  # "list" | "detail" | "add" | "edit"
if "er_selected_id" not in st.session_state:
    st.session_state.er_selected_id = None
if "er_edit_id" not in st.session_state:
    st.session_state.er_edit_id = None


def _go_list() -> None:
    st.session_state.er_view = "list"
    st.session_state.er_selected_id = None
    st.session_state.er_edit_id = None


def _go_detail(entity_id: int) -> None:
    st.session_state.er_view = "detail"
    st.session_state.er_selected_id = entity_id


def _go_add() -> None:
    st.session_state.er_view = "add"


def _go_edit(entity_id: int) -> None:
    st.session_state.er_view = "edit"
    st.session_state.er_edit_id = entity_id


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _api_error(exc: Exception) -> None:
    """Display an API error and stop."""
    if isinstance(exc, ConnectionError):
        st.error(
            "Could not connect to the API server. "
            "Make sure the backend is running."
        )
    else:
        st.error(f"API error: {exc}")


def _entity_form(
    *,
    key_prefix: str,
    defaults: dict | None = None,
) -> dict | None:
    """Render an entity creation/edit form. Returns payload dict on submit."""
    d = defaults or {}
    with st.form(f"{key_prefix}_entity_form"):
        name = st.text_input("Name *", value=d.get("name", ""))
        jurisdiction = st.text_input(
            "Jurisdiction *", value=d.get("jurisdiction", "")
        )
        type_idx = (
            ENTITY_TYPES.index(d["entity_type"])
            if d.get("entity_type") in ENTITY_TYPES
            else 0
        )
        entity_type = st.selectbox("Entity Type *", ENTITY_TYPES, index=type_idx)
        formation_date = st.date_input(
            "Formation Date",
            value=d.get("formation_date"),
        )
        good_standing = st.checkbox(
            "Good Standing",
            value=d.get("good_standing", True),
        )
        registered_agent = st.text_input(
            "Registered Agent", value=d.get("registered_agent", "") or ""
        )
        ein = st.text_input("EIN", value=d.get("ein", "") or "")
        notes = st.text_area("Notes", value=d.get("notes", "") or "")

        submitted = st.form_submit_button("Save")
        if submitted:
            if not name or not jurisdiction:
                st.warning("Name and Jurisdiction are required.")
                return None
            payload: dict = {
                "name": name,
                "jurisdiction": jurisdiction,
                "entity_type": entity_type,
                "formation_date": str(formation_date) if formation_date else None,
                "good_standing": good_standing,
                "registered_agent": registered_agent or None,
                "ein": ein or None,
                "notes": notes or None,
            }
            return payload
    return None


# =====================================================================
# VIEW: ADD ENTITY
# =====================================================================
if st.session_state.er_view == "add":
    st.subheader("Add New Entity")
    if st.button("Cancel", key="add_cancel"):
        _go_list()
        st.rerun()

    payload = _entity_form(key_prefix="add")
    if payload is not None:
        try:
            client.post("/api/entities/", json=payload)
            st.success("Entity created.")
            _go_list()
            st.rerun()
        except RequestException as exc:
            _api_error(exc)

# =====================================================================
# VIEW: EDIT ENTITY
# =====================================================================
elif st.session_state.er_view == "edit":
    eid = st.session_state.er_edit_id
    st.subheader("Edit Entity")
    if st.button("Cancel", key="edit_cancel"):
        _go_detail(eid)
        st.rerun()

    try:
        entity = client.get(f"/api/entities/{eid}")
    except RequestException as exc:
        _api_error(exc)
        st.stop()

    payload = _entity_form(key_prefix="edit", defaults=entity)
    if payload is not None:
        try:
            client.put(f"/api/entities/{eid}", json=payload)
            st.success("Entity updated.")
            _go_detail(eid)
            st.rerun()
        except RequestException as exc:
            _api_error(exc)

# =====================================================================
# VIEW: ENTITY DETAIL
# =====================================================================
elif st.session_state.er_view == "detail":
    eid = st.session_state.er_selected_id
    if st.button("Back to List", key="detail_back"):
        _go_list()
        st.rerun()

    try:
        entity: dict = client.get(f"/api/entities/{eid}")
    except RequestException as exc:
        _api_error(exc)
        st.stop()

    # --- Entity header ---------------------------------------------------
    st.subheader(entity.get("name", ""))
    info_cols = st.columns(4)
    info_cols[0].markdown(f"**Jurisdiction:** {entity.get('jurisdiction', '')}")
    info_cols[1].markdown(f"**Type:** {entity.get('entity_type', '')}")
    info_cols[2].markdown(
        f"**Good Standing:** {'Yes' if entity.get('good_standing') else 'No'}"
    )
    info_cols[3].markdown(
        f"**Formation Date:** {format_date(entity.get('formation_date'))}"
    )

    if entity.get("registered_agent"):
        st.markdown(f"**Registered Agent:** {entity['registered_agent']}")
    if entity.get("ein"):
        st.markdown(f"**EIN:** {entity['ein']}")
    if entity.get("notes"):
        st.markdown(f"**Notes:** {entity['notes']}")

    btn_cols = st.columns([1, 1, 6])
    if btn_cols[0].button("Edit Entity", key="detail_edit"):
        _go_edit(eid)
        st.rerun()
    if btn_cols[1].button("Delete Entity", key="detail_delete"):
        st.session_state.er_confirm_delete = True

    if st.session_state.get("er_confirm_delete"):
        st.warning("Are you sure you want to delete this entity?")
        cc1, cc2, _ = st.columns([1, 1, 6])
        if cc1.button("Yes, delete", key="confirm_yes"):
            try:
                client.delete(f"/api/entities/{eid}")
                st.success("Entity deleted.")
                st.session_state.er_confirm_delete = False
                _go_list()
                st.rerun()
            except RequestException as exc:
                _api_error(exc)
        if cc2.button("Cancel", key="confirm_no"):
            st.session_state.er_confirm_delete = False
            st.rerun()

    st.divider()

    # --- Tabs ------------------------------------------------------------
    tab_officers, tab_filings, tab_docs = st.tabs(
        ["Officers & Directors", "Filing Deadlines", "Governance Documents"]
    )

    # ---- Officers tab ---------------------------------------------------
    with tab_officers:
        try:
            officers: list[dict] = client.get(f"/api/entities/{eid}/officers")
        except RequestException as exc:
            _api_error(exc)
            officers = []

        if officers:
            header = (
                "| Name | Title | Role | Term Start | Term End | Email |\n"
                "|------|-------|------|------------|----------|-------|\n"
            )
            rows = ""
            for o in officers:
                rows += (
                    f"| {o.get('name', '')} | {o.get('title', '')} "
                    f"| {o.get('role', '')} | {format_date(o.get('term_start'))} "
                    f"| {format_date(o.get('term_end'))} | {o.get('email', '')} |\n"
                )
            st.markdown(header + rows)
        else:
            st.info("No officers or directors recorded.")

        # Add officer form
        with st.expander("Add Officer / Director"):
            with st.form("add_officer_form"):
                o_name = st.text_input("Name *", key="off_name")
                o_title = st.text_input("Title", key="off_title")
                o_role = st.text_input("Role", key="off_role")
                oc1, oc2 = st.columns(2)
                o_start = oc1.date_input("Term Start", value=None, key="off_start")
                o_end = oc2.date_input("Term End", value=None, key="off_end")
                o_email = st.text_input("Email", key="off_email")
                if st.form_submit_button("Add Officer"):
                    if not o_name:
                        st.warning("Name is required.")
                    else:
                        payload = {
                            "name": o_name,
                            "title": o_title or None,
                            "role": o_role or None,
                            "term_start": str(o_start) if o_start else None,
                            "term_end": str(o_end) if o_end else None,
                            "email": o_email or None,
                        }
                        try:
                            client.post(
                                f"/api/entities/{eid}/officers", json=payload
                            )
                            st.success("Officer added.")
                            st.rerun()
                        except RequestException as exc:
                            _api_error(exc)

        # Delete officer
        if officers:
            with st.expander("Remove Officer"):
                officer_options = {
                    f"{o['name']} ({o.get('title', '')})": o["id"]
                    for o in officers
                }
                sel = st.selectbox(
                    "Select officer to remove",
                    list(officer_options.keys()),
                    key="del_officer_sel",
                )
                if st.button("Delete Officer", key="del_officer_btn"):
                    try:
                        client.delete(f"/api/officers/{officer_options[sel]}")
                        st.success("Officer removed.")
                        st.rerun()
                    except RequestException as exc:
                        _api_error(exc)

    # ---- Filings tab ----------------------------------------------------
    with tab_filings:
        try:
            filings: list[dict] = client.get(f"/api/entities/{eid}/filings")
        except RequestException as exc:
            _api_error(exc)
            filings = []

        if filings:
            table_html = """
            <table style="width:100%;border-collapse:collapse;">
            <thead>
            <tr style="text-align:left;border-bottom:2px solid #ddd;">
                <th style="padding:8px;">Type</th>
                <th style="padding:8px;">Jurisdiction</th>
                <th style="padding:8px;">Due Date</th>
                <th style="padding:8px;">Status</th>
                <th style="padding:8px;">Filed Date</th>
            </tr>
            </thead><tbody>
            """
            for f in filings:
                due = f.get("due_date", "")
                status = f.get("status", "pending")
                badge = urgency_badge(due, status) if due else status
                table_html += f"""
                <tr style="border-bottom:1px solid #eee;">
                    <td style="padding:8px;">{f.get('filing_type', '')}</td>
                    <td style="padding:8px;">{f.get('jurisdiction', '')}</td>
                    <td style="padding:8px;">{format_date(due)}</td>
                    <td style="padding:8px;">{badge}</td>
                    <td style="padding:8px;">{format_date(f.get('filed_date'))}</td>
                </tr>
                """
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)

            # Mark as Filed
            pending = [
                f
                for f in filings
                if f.get("status", "").lower() != "filed"
            ]
            if pending:
                with st.expander("Mark Filing as Filed"):
                    filing_options = {
                        f"{f['filing_type']} — due {format_date(f.get('due_date'))}": f[
                            "id"
                        ]
                        for f in pending
                    }
                    sel_f = st.selectbox(
                        "Select filing",
                        list(filing_options.keys()),
                        key="mark_filed_sel",
                    )
                    if st.button("Mark as Filed", key="mark_filed_btn"):
                        try:
                            client.post(
                                f"/api/filings/{filing_options[sel_f]}/mark-filed"
                            )
                            st.success("Filing marked as filed.")
                            st.rerun()
                        except RequestException as exc:
                            _api_error(exc)
        else:
            st.info("No filing deadlines recorded.")

        # Add filing form
        with st.expander("Add Filing Deadline"):
            with st.form("add_filing_form"):
                f_type = st.text_input("Filing Type *", key="fil_type")
                f_jur = st.text_input("Jurisdiction", key="fil_jur")
                f_due = st.date_input("Due Date *", key="fil_due")
                f_status = st.selectbox(
                    "Status",
                    ["pending", "filed", "overdue"],
                    key="fil_status",
                )
                if st.form_submit_button("Add Filing"):
                    if not f_type:
                        st.warning("Filing Type is required.")
                    else:
                        payload = {
                            "filing_type": f_type,
                            "jurisdiction": f_jur or None,
                            "due_date": str(f_due) if f_due else None,
                            "status": f_status,
                        }
                        try:
                            client.post(
                                f"/api/entities/{eid}/filings", json=payload
                            )
                            st.success("Filing added.")
                            st.rerun()
                        except RequestException as exc:
                            _api_error(exc)

        # Delete filing
        if filings:
            with st.expander("Remove Filing"):
                filing_del_opts = {
                    f"{f['filing_type']} — due {format_date(f.get('due_date'))}": f[
                        "id"
                    ]
                    for f in filings
                }
                sel_fd = st.selectbox(
                    "Select filing to remove",
                    list(filing_del_opts.keys()),
                    key="del_filing_sel",
                )
                if st.button("Delete Filing", key="del_filing_btn"):
                    try:
                        client.delete(f"/api/filings/{filing_del_opts[sel_fd]}")
                        st.success("Filing removed.")
                        st.rerun()
                    except RequestException as exc:
                        _api_error(exc)

    # ---- Documents tab --------------------------------------------------
    with tab_docs:
        try:
            docs: list[dict] = client.get(f"/api/entities/{eid}/documents")
        except RequestException as exc:
            _api_error(exc)
            docs = []

        if docs:
            header = (
                "| Title | Type | URL | Description |\n"
                "|-------|------|-----|-------------|\n"
            )
            rows = ""
            for doc in docs:
                url = doc.get("url", "")
                url_cell = f"[Link]({url})" if url else ""
                rows += (
                    f"| {doc.get('title', '')} | {doc.get('document_type', '')} "
                    f"| {url_cell} | {doc.get('description', '') or ''} |\n"
                )
            st.markdown(header + rows)
        else:
            st.info("No governance documents recorded.")

        # Add document form
        with st.expander("Add Document"):
            with st.form("add_doc_form"):
                d_title = st.text_input("Title *", key="doc_title")
                d_type = st.text_input("Document Type", key="doc_type")
                d_url = st.text_input("URL", key="doc_url")
                d_desc = st.text_area("Description", key="doc_desc")
                if st.form_submit_button("Add Document"):
                    if not d_title:
                        st.warning("Title is required.")
                    else:
                        payload = {
                            "title": d_title,
                            "document_type": d_type or None,
                            "url": d_url or None,
                            "description": d_desc or None,
                        }
                        try:
                            client.post(
                                f"/api/entities/{eid}/documents", json=payload
                            )
                            st.success("Document added.")
                            st.rerun()
                        except RequestException as exc:
                            _api_error(exc)

        # Delete document
        if docs:
            with st.expander("Remove Document"):
                doc_del_opts = {
                    doc.get("title", f"doc-{doc['id']}"): doc["id"]
                    for doc in docs
                }
                sel_doc = st.selectbox(
                    "Select document to remove",
                    list(doc_del_opts.keys()),
                    key="del_doc_sel",
                )
                if st.button("Delete Document", key="del_doc_btn"):
                    try:
                        client.delete(f"/api/documents/{doc_del_opts[sel_doc]}")
                        st.success("Document removed.")
                        st.rerun()
                    except RequestException as exc:
                        _api_error(exc)

# =====================================================================
# VIEW: LIST (default)
# =====================================================================
else:
    # --- Sidebar filters -------------------------------------------------
    st.sidebar.header("Filters")
    filter_jurisdiction = st.sidebar.text_input("Jurisdiction", key="er_filt_jur")
    filter_type = st.sidebar.selectbox(
        "Entity Type",
        ["All"] + ENTITY_TYPES,
        key="er_filt_type",
    )
    filter_search = st.sidebar.text_input("Search", key="er_filt_search")

    if st.button("Add New Entity", key="list_add"):
        _go_add()
        st.rerun()

    # --- Fetch entities --------------------------------------------------
    params: dict = {}
    if filter_jurisdiction:
        params["jurisdiction"] = filter_jurisdiction
    if filter_type != "All":
        params["entity_type"] = filter_type
    if filter_search:
        params["search"] = filter_search

    try:
        entities: list[dict] = client.get("/api/entities/", params=params)
    except ConnectionError:
        st.error("Could not connect to the API server.")
        st.stop()
    except RequestException as exc:
        st.error(f"API error: {exc}")
        st.stop()

    if not entities:
        st.info("No entities found. Add one to get started!")
        st.stop()

    # --- Entity selector -------------------------------------------------
    entity_names = {
        f"{e['name']} ({e.get('jurisdiction', '')})" : e["id"]
        for e in entities
    }

    st.subheader(f"Entities ({len(entities)})")

    # Table
    header = (
        "| Name | Jurisdiction | Type | Good Standing | Formation Date |\n"
        "|------|-------------|------|---------------|----------------|\n"
    )
    rows = ""
    for e in entities:
        gs = "Yes" if e.get("good_standing") else "No"
        rows += (
            f"| {e.get('name', '')} | {e.get('jurisdiction', '')} "
            f"| {e.get('entity_type', '')} | {gs} "
            f"| {format_date(e.get('formation_date'))} |\n"
        )
    st.markdown(header + rows)

    # Select entity to view details
    st.subheader("View Entity Details")
    selected_label = st.selectbox(
        "Select an entity",
        list(entity_names.keys()),
        key="er_entity_select",
    )
    if st.button("View Details", key="list_view_detail"):
        _go_detail(entity_names[selected_label])
        st.rerun()
