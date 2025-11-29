import time

import streamlit as st

from services.analyze import run_analysis, to_dict
from utils.pdf_utils import show_pdf
from components.history import add_to_history
from utils.style_utils import inject_global_styles


def render_upload():
    inject_global_styles()

    st.subheader("Rapor Yükle")

    if "preview_open" not in st.session_state:
        st.session_state.preview_open = False
    if "job_done" not in st.session_state:
        st.session_state.job_done = False

    role = st.session_state.get("user_role", "student")

    uploaded = st.file_uploader(
        "PDF veya DOCX yükleyin",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=False,
    )

    if uploaded and not st.session_state.job_done:
        st.session_state.preview_open = True

    if uploaded:
        toggle_label = (
            "Önizlemeyi Gizle" if st.session_state.preview_open else "Önizlemeyi Göster"
        )
        if st.button(toggle_label):
            st.session_state.preview_open = not st.session_state.preview_open
            st.rerun()

    if uploaded and st.session_state.preview_open:
        if uploaded.type == "application/pdf":
            uploaded.seek(0)
            show_pdf(uploaded.read(), width=900, height=800)
        else:
            st.write("PDF önizleme yalnızca .pdf dosyaları için desteklenir.")

    analyze_btn = st.button("Analiz Et", type="primary")

    if role == "student":
        st.caption("Öğrenciler sadece feedback görebilir, sayısal puanlar gösterilmez.")

    if analyze_btn:
        if not uploaded:
            st.error("Lütfen PDF/DOCX dosyası yükleyin.")
            return

        st.session_state.preview_open = False
        st.session_state.job_done = False

        st.markdown(
            '<div class="overlay"><div class="spinner"></div><p>Analiz yapılıyor...</p></div>',
            unsafe_allow_html=True,
        )

        uploaded.seek(0)

        with st.status("Analiz başlatıldı...", expanded=True) as status:
            st.write("Dosya okunuyor...")
            time.sleep(0.3)

            file_bytes = uploaded.read()

            st.write("Model çalışıyor...")
            for pct in range(0, 101, 20):
                st.progress(pct)
                time.sleep(0.2)

            st.write("Sonuçlar hesaplanıyor...")
            time.sleep(0.3)

            result = run_analysis(file_bytes, uploaded.name)
            result_dict = to_dict(result)

            st.session_state.results = result_dict
            st.session_state.job_done = True

            total_for_history = result_dict.get("total", 0)
            add_to_history(uploaded.name, total_for_history)

            status.update(label="Analiz tamamlandı.", state="complete")
            time.sleep(0.6)
            st.rerun()
