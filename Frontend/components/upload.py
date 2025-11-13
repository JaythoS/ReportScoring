import streamlit as st
import time
from Frontend.src.analyze import run_mock_analysis, to_dict
from Frontend.utils.pdf_utils import show_pdf
from Frontend.utils.style_utils import inject_global_styles
from Frontend.components.history import add_to_history


def render_upload():
    """
    1) PDF/DOCX yükleme
    2) PDF önizleme: upload olunca otomatik AÇILIR, analiz başlayınca otomatik KAPANIR
    3) Analiz tetikleme + overlay spinner
    4) Analiz sonucunu session_state'e kaydetme
    5) Geçmişe kayıt ekleme
    """
    inject_global_styles()

    st.subheader(" 1) Raporu Yükle")

    # session_state setup
    if "preview_open" not in st.session_state:
        st.session_state.preview_open = False
    if "job_done" not in st.session_state:
        st.session_state.job_done = False

    uploaded = st.file_uploader(
        "PDF veya DOCX yükle",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=False
    )

    # PDF yüklendiğinde otomatik önizlemeyi aç
    if uploaded and not st.session_state.preview_open:
        st.session_state.preview_open = True

    # PDF önizleme toggle
    if uploaded:
        toggle_label = " Önizlemeyi Gizle" if st.session_state.preview_open else " Önizlemeyi Göster"
        if st.button(toggle_label):
            st.session_state.preview_open = not st.session_state.preview_open
            st.rerun()

    # PDF önizleme açıkken göster
    if uploaded and st.session_state.preview_open:
        if uploaded.type == "application/pdf":
            uploaded.seek(0)
            show_pdf(uploaded.read(), width=900, height=800)

        else:
            st.info("PDF önizleme sadece .pdf dosyaları için aktiftir.")

    analyze_btn = st.button(" Yükle ve Analiz Et", type="primary")

    if analyze_btn:
        if not uploaded:
            st.error(" Lütfen PDF/DOCX dosyası yükleyin.")
            return
        elif uploaded.size and uploaded.size > 15 * 1024 * 1024:
            st.error(" Dosya 15MB’ı aşıyor. Lütfen daha küçük bir dosya deneyin.")
            return

        # Önizlemeyi otomatik kapat
        st.session_state.preview_open = False

        # Overlay spinner
        st.markdown(
            '<div class="overlay"><div class="spinner"></div><p>Analiz yapılıyor…</p></div>',
            unsafe_allow_html=True
        )

        with st.status("Analiz başlatıldı...", expanded=True) as status:
            st.write(" Dosya okunuyor…")
            time.sleep(0.3)
            st.write(" Model (mock) çalışıyor…")
            for pct in range(0, 101, 20):
                st.progress(pct)
                time.sleep(0.2)
            st.write(" Sonuçlar hesaplanıyor…")
            time.sleep(0.3)

            result = run_mock_analysis(uploaded.read())
            result_dict = to_dict(result)
            st.session_state.results = result_dict
            st.session_state.job_done = True

            add_to_history(uploaded.name, result_dict.get("total", 0.0))

            status.update(label=" Analiz tamamlandı!", state="complete")
            time.sleep(0.6)
            st.rerun()
