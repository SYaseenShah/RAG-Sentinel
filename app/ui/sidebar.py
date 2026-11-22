import streamlit as st
from security.auth import has_role
from security.audit import log_event
from app.ui.components import render_html


NAV_ITEMS = [
    {"id": "Security Overview", "label": "Security Overview", "icon": "🛡️", "roles": ["viewer", "analyst", "admin"]},
    {"id": "Document Security", "label": "Document Security", "icon": "📄", "roles": ["analyst", "admin"]},
    {"id": "Protected AI Chat", "label": "Protected AI Chat", "icon": "💬", "roles": ["viewer", "analyst", "admin"]},
    {"id": "Quarantine Center", "label": "Quarantine Center", "icon": "☣️", "roles": ["admin"]},
    {"id": "Research Lab", "label": "Research Lab", "icon": "🔬", "roles": ["analyst", "admin"]},
    {"id": "Evaluation & Reports", "label": "Evaluation & Reports", "icon": "📊", "roles": ["analyst", "admin"]},
    {"id": "User & Audit Administration", "label": "Administration", "icon": "⚙️", "roles": ["admin"]},
]


def render_sidebar(current_user: dict) -> str:
    """Render the Google Stitch operational sidebar and return the selected page key."""
    role = current_user.get("role", "viewer")

    # Filter allowed navigation items by user role
    allowed_items = [
        item for item in NAV_ITEMS
        if any(has_role(current_user, r) for r in item["roles"])
    ]

    with st.sidebar:
        # Brand Header
        brand_html = """
<div class="sidebar-brand">
<div class="brand-icon">🛡️</div>
<div>
<div class="brand-title">RAG SENTINEL</div>
<div class="brand-sub">AI SOC v3.4</div>
</div>
</div>
"""
        render_html(brand_html)

        render_html('<div class="nav-section-title">Operational Modules</div>')

        # Radio navigation with icons matching Stitch design
        options = [item["id"] for item in allowed_items]
        format_dict = {item["id"]: f"{item['icon']}  {item['label']}" for item in allowed_items}

        selected_page = st.radio(
            "OPERATIONAL MODULES",
            options=options,
            format_func=lambda opt: format_dict.get(opt, opt),
            label_visibility="collapsed",
            key="rag_sentinel_nav_page",
        )

        st.write("")

        # Sign-out action
        if st.button("Sign Out", use_container_width=True, key="sidebar_sign_out_btn"):
            log_event(current_user.get("username", "unknown"), "logout", {"role": role})
            st.session_state["authenticated_user"] = None
            st.rerun()

        # Telemetry Footer
        telemetry_html = """
<div class="sidebar-footer">
<div class="telemetry-row">
<span class="telemetry-label">Cluster Grid</span>
<span class="telemetry-val" style="display:flex;align-items:center;gap:5px;">
<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#10b981;box-shadow:0 0 6px #10b981;"></span>
Online
</span>
</div>
<div class="telemetry-row" style="margin-top:4px;">
<span class="telemetry-label" style="font-size:0.68rem;">VectorShield-US-East</span>
</div>
<div class="telemetry-row" style="margin-top:4px;">
<span class="telemetry-label">Integrity</span>
<span class="telemetry-val">Nominal 99.98%</span>
</div>
</div>
"""
        render_html(telemetry_html)

    return selected_page
