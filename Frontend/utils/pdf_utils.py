import base64
import streamlit as st

# pdf.js modülünü dene
try:
    from streamlit_pdf_viewer import pdf_viewer
    PDF_VIEWER_AVAILABLE = True
except ImportError:
    PDF_VIEWER_AVAILABLE = False


def show_pdf(file_bytes: bytes, width: int = 900, height: int = 800):
    """
    PDF'yi sayfa içinde görüntüler.
    1️ streamlit-pdf-viewer varsa pdf.js ile gösterir.
    2️ yoksa HTML <iframe> fallback kullanır.
    """

    if PDF_VIEWER_AVAILABLE:
        st.markdown("** PDF Önizleme (pdf.js viewer)**")
        pdf_viewer(file_bytes, width=width, height=height)
        return

    # base64 fallback (garanti çalışır)
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
    st.markdown("** PDF Önizleme (iframe fallback)**")
    st.components.v1.html(html_code, height=height + 20, scrolling=True)
