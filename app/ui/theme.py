from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
THEME_CSS_PATH = ROOT / "assets" / "css" / "theme.css"


def inject_custom_theme():
    """Load and inject the Google Stitch cybersecurity theme CSS into Streamlit."""
    if THEME_CSS_PATH.is_file():
        css = THEME_CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
