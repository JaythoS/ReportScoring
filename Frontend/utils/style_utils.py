import streamlit as st
from pathlib import Path

def inject_global_styles():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "spinner.css"

    css_content = ""
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    st.markdown(
        f"""
        <style>
        {css_content}

        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1150px;
        }}

        .section-card {{
            background: #0f172a;
            border: 1px solid #1f2937;
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 18px;
        }}

        h1, h2, h3, h4 {{
            letter-spacing: 0.2px;
            color: #e2e8f0;
        }}

        .stMetric {{
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 14px;
            padding: 12px 16px;
        }}

        .stDataFrame {{
            background: #1e293b;
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
