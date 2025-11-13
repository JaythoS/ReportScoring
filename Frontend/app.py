import streamlit as st

# Component'leri import et
from Frontend.components.upload import render_upload
from Frontend.components.results import render_results
from Frontend.components.dashboard import render_dashboard
from Frontend.components.history import render_history

from Frontend.utils.style_utils import inject_global_styles


# Sayfa başlığı ve layout
st.set_page_config(page_title="Rapor Değerlendirme", layout="wide")

# Global stilleri yükle
inject_global_styles()

# Başlık
st.title(" Bitirme • Rapor Değerlendirme Arayüzü")
st.caption("Upload → Analiz → Sonuçlar → Dashboard → Geçmiş")

# Session state başlangıçları
if "job_done" not in st.session_state:
    st.session_state.job_done = False
if "results" not in st.session_state:
    st.session_state.results = None
if "history" not in st.session_state:
    st.session_state.history = []
if "auto_closed" not in st.session_state:
    st.session_state.auto_closed = True

# Tab sistemi
tab1, tab2, tab3 = st.tabs([" Analiz", " Dashboard", " Geçmiş Analizler"])

# --- TAB 1: Upload + Sonuçlar ---
with tab1:
    st.markdown("### 🔹 Analiz Akışı")
    render_upload()
    st.divider()
    render_results()

# --- TAB 2: Dashboard ---
with tab2:
    render_dashboard(st.session_state.get("results"))

# --- TAB 3: Geçmiş Analizler ---
with tab3:
    render_history()

# Footer
st.markdown("---")
st.caption("© 2025 Bitirme Projesi • FE by Umut & Helin")
