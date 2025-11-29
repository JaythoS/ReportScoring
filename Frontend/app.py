from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from auth import ensure_authenticated
from components.upload import render_upload
from components.results import render_results
from components.dashboard import render_dashboard
from components.history import render_history
from utils.style_utils import inject_global_styles


st.set_page_config(page_title="Rapor Değerlendirme", layout="wide")

inject_global_styles()

email, role = ensure_authenticated()

st.title("Rapor Değerlendirme Arayüzü")
st.write(f"Giriş yapılan hesap: {email} | Rol: {role}")

# STATE INIT
if "job_done" not in st.session_state:
    st.session_state.job_done = False
if "results" not in st.session_state:
    st.session_state.results = None
if "history" not in st.session_state:
    st.session_state.history = []
if "auto_closed" not in st.session_state:
    st.session_state.auto_closed = True

# TABS ROLE-BASED
if role in ["admin", "teacher"]:
    tab1, tab2, tab3 = st.tabs(["Analiz", "Dashboard", "Geçmiş"])
else:
    tab1, = st.tabs(["Analiz"])
    tab2 = None
    tab3 = None

# TAB 1 – ANALİZ
with tab1:
    render_upload()

    # ADMIN + TEACHER sonuçları tam görür
    if role in ["admin", "teacher"]:
        render_results()
    else:
        st.write("Öğrenciler sadece feedback görebilir.")

# TAB 2 – DASHBOARD (only admin/teacher)
if role in ["admin", "teacher"] and tab2 is not None:
    with tab2:
        render_dashboard(st.session_state.get("results"))

# TAB 3 – HISTORY (only admin/teacher)
if role in ["admin", "teacher"] and tab3 is not None:
    with tab3:
        render_history()

st.write("---")
