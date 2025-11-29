import base64
import streamlit as st

try:
    from streamlit_pdf_viewer import pdf_viewer
    PDF_VIEWER_AVAILABLE = True
except Exception:
    PDF_VIEWER_AVAILABLE = False


def show_pdf(file_bytes: bytes, width: int = 900, height: int = 800):
    if PDF_VIEWER_AVAILABLE:
        pdf_viewer(file_bytes, width=width, height=height)
        return

    b64 = base64.b64encode(file_bytes).decode("utf-8")

    html_code = f"""
    <iframe
        src="data:application/pdf;base64,{b64}#view=FitH"
        width="{width}"
        height="{height}"
        type="application/pdf"
        style="border:none;border-radius:10px;"
    ></iframe>
    """

    st.components.v1.html(html_code, height=height + 20, scrolling=True)
