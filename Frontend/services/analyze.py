import requests
from services.mock_data import MOCK_ANALYSIS
import streamlit as st


def run_analysis(file_bytes, filename):
    use_mock = st.secrets.get("USE_MOCK", True)

    if use_mock:
        return MOCK_ANALYSIS

    backend_url = st.secrets["api"]["analyze_url"]

    try:
        files = {"file": (filename, file_bytes, "application/pdf")}
        response = requests.post(backend_url, files=files, timeout=40)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {
            "total": 0,
            "sections": []
        }


def to_dict(result):
    if not isinstance(result, dict):
        return {"total": 0, "sections": []}

    sections = result.get("sections", [])
    total = result.get("total")

    if total is None and sections:
        scores = [int(s.get("score", 0)) for s in sections]
        total = sum(scores)
        result["total"] = total

    return {
        "total": total or 0,
        "sections": sections
    }
