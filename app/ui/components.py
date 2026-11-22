"""Reusable UI components implementing the Google Stitch design system."""

import streamlit as st


def render_html(html_str: str):
    """Safely render raw HTML in Streamlit by stripping all leading line whitespace.
    
    This prevents CommonMark markdown parsers from treating 4-space indented HTML as code blocks.
    """
    clean_lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    cleaned = "\n".join(clean_lines)
    st.markdown(cleaned, unsafe_allow_html=True)


def render_page_header(
    kicker: str,
    title: str,
    subtitle: str,
    kicker_icon: str = "●",
    actions_html: str = "",
):
    """Render a Google Stitch styled section/page header with kicker, title, and subtitle."""
    header_html = f"""
<div class="stitch-page-header">
<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
<div>
<div class="header-kicker-wrap">
<span style="color:#00f0ff;font-size:0.68rem;">{kicker_icon}</span>
<span class="header-kicker">{kicker}</span>
</div>
<h1 class="header-title">{title}</h1>
<p class="header-subtitle">{subtitle}</p>
</div>
<div>
{actions_html}
</div>
</div>
</div>
"""
    render_html(header_html)


def render_kpi_card(
    label: str,
    value: str | int,
    icon: str = "🛡️",
    badge_text: str = "",
    badge_type: str = "emerald",  # emerald, rose, amber, cyan, purple, neutral
    subtitle: str = "",
):
    """Render a cybersecurity KPI metric card with icon, badge, and metadata footer."""
    badge_html = f'<span class="stitch-badge badge-{badge_type}">{badge_text}</span>' if badge_text else ""
    subtitle_html = f'<span style="color:var(--text-muted);font-size:0.75rem;">{subtitle}</span>' if subtitle else ""

    card_html = f"""
<div class="stitch-kpi-card">
<div>
<div class="kpi-top">
<span class="kpi-label">{label}</span>
<div class="kpi-icon-box" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);">
{icon}
</div>
</div>
<div class="kpi-val">{value}</div>
</div>
<div class="kpi-bottom">
{badge_html}
{subtitle_html}
</div>
</div>
"""
    render_html(card_html)


def render_status_badge(text: str, badge_type: str = "cyan") -> str:
    """Return HTML string for an inline security status badge."""
    return f'<span class="stitch-badge badge-{badge_type}">{text}</span>'


def render_pipeline_stepper(stages: list[dict], active_stage: int = 1):
    """Render the RAG Ingestion Security Pipeline multi-step visualization without any markdown code escaping."""
    steps_html = []
    for stage in stages:
        status = stage.get("status", "pending")
        if status == "done":
            border_style = "border-color: rgba(16,185,129,0.35); background: rgba(16,185,129,0.04);"
            indicator = '<span style="color:#10b981;font-weight:700;">✓</span>'
        elif status == "active":
            border_style = "border-color: rgba(0,240,255,0.5); background: rgba(0,240,255,0.06); box-shadow: 0 0 12px rgba(0,240,255,0.15);"
            indicator = '<span class="pulsing-dot dot-cyan" style="display:inline-block;"></span>'
        else:
            border_style = "border-color: var(--border-subtle); background: #090f1a;"
            indicator = '<span style="color:var(--text-dim);">○</span>'

        badge_txt = stage.get("badge", "")
        badge_html = f'<span class="stitch-badge badge-neutral" style="font-size:0.6rem;padding:1px 5px;">{badge_txt}</span>' if badge_txt else ""

        step_html = f"""
<div class="pipeline-step" style="{border_style}">
<div class="step-num">
<span>{stage.get('num', '01')} / STAGE</span>
<span>{indicator}</span>
</div>
<div class="step-name">{stage.get('name', '')}</div>
<div class="step-desc">{stage.get('desc', '')}</div>
<div style="margin-top:6px;">{badge_html}</div>
</div>
"""
        steps_html.append(step_html.strip())

    all_steps = "".join(steps_html)

    pipeline_card_html = f"""
<div class="stitch-pipeline-card">
<div class="pipeline-header">
<div class="pipeline-title">
<span style="color:#00f0ff;">⚡</span>
<span>RAG Ingestion Security Pipeline</span>
</div>
<div>
<span class="stitch-badge badge-cyan">Active Stream · 240 Chunks/Sec</span>
<span class="stitch-badge badge-emerald" style="margin-left:6px;">Stage Latency: 142ms Nominal</span>
</div>
</div>
<div class="pipeline-steps">
{all_steps}
</div>
</div>
"""
    render_html(pipeline_card_html)


def render_security_callout(title: str, text: str, level: str = "info"):
    """Render a cybersecurity advisory callout."""
    level_colors = {
        "info": ("#00f0ff", "rgba(0,240,255,0.06)", "rgba(0,240,255,0.3)"),
        "success": ("#10b981", "rgba(16,185,129,0.06)", "rgba(16,185,129,0.3)"),
        "warning": ("#f59e0b", "rgba(245,158,11,0.06)", "rgba(245,158,11,0.3)"),
        "danger": ("#f43f5e", "rgba(244,63,94,0.06)", "rgba(244,63,94,0.3)"),
    }
    color, bg, border = level_colors.get(level, level_colors["info"])
    callout_html = f"""
<div style="background:{bg};border:1px solid {border};border-left:4px solid {color};border-radius:8px;padding:12px 16px;margin:12px 0;">
<div style="font-family:var(--font-mono);font-size:0.75rem;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">
{title}
</div>
<div style="font-size:0.85rem;color:var(--text-secondary);line-height:1.45;">
{text}
</div>
</div>
"""
    render_html(callout_html)
