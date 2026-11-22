import streamlit as st
from app.ui.components import render_html


def render_top_navbar(current_user: dict | None = None):
    """Render the Google Stitch top navigation bar with search, DEFCON status, radar & user profile."""
    username = current_user.get("username", "Analyst") if current_user else "SecOps"
    role = (current_user.get("role", "admin") if current_user else "admin").upper()
    role_label = "Lead SecOps Architect" if role == "ADMIN" else f"SecOps {role.capitalize()}"
    avatar_initials = username[:2].upper() if username else "SO"

    navbar_html = f"""
<div class="stitch-topbar">
<div class="topbar-search-box">
<span style="color:#00f0ff;font-size:0.9rem;">🔍</span>
<span>Search vectors, CVEs, documents...</span>
<span class="topbar-shortcut">⌘K</span>
</div>
<div class="topbar-badges">
<div class="topbar-status-pill status-radar">
<div class="pulsing-dot dot-cyan"></div>
<span>Threat Radar</span>
</div>
<div class="topbar-status-pill status-defcon">
<div class="pulsing-dot dot-emerald"></div>
<span>DEFCON 4 · Guarded</span>
</div>
<div style="position:relative;cursor:pointer;padding:4px 8px;font-size:1.05rem;" title="3 Active Security Notifications">
🔔
<span style="position:absolute;top:0;right:2px;background:#f43f5e;color:#fff;font-size:0.6rem;font-weight:700;padding:1px 4px;border-radius:10px;line-height:1;">3</span>
</div>
<div class="topbar-profile">
<div class="profile-avatar">{avatar_initials}</div>
<div>
<div class="profile-name">{username.capitalize()}</div>
<div class="profile-role">{role_label}</div>
</div>
</div>
</div>
</div>
"""
    render_html(navbar_html)
