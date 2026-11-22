"""RAG Sentinel — Streamlit Community Cloud Root Entry Point.

This root entry point forwards execution to app/main.py, allowing deployment
whether Streamlit Cloud is configured with 'streamlit_app.py' or 'app/main.py'.
"""
import sys
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

target_app = ROOT / "app" / "main.py"
runpy.run_path(str(target_app), run_name="__main__")
