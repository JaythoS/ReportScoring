import time
import pandas as pd
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer  
from src.analyze import run_mock_analysis, to_dict

st.set_page_config(page_title="Rapor Değerlendirme", layout="wide")

# Küçük stil dokunuşu
st.markdown("""
    <style>
    .stMetric { background:#f8fafc; padding:10px; border-radius:12px; }
    .viewer-title { font-weight:600; font-size:16px; margin-top:8px; }
    </style>
""", unsafe_allow_html=True)

st.title(" Rapor Değerlendirme")
st.caption("Upload → Analiz Durumu → Sonuç Tablosu | *Mock analiz ile başlangıç*")

# Session init
if "job_done" not in st.session_state:
    st.session_state.job_done = False
if "results" not in st.session_state:
    st.session_state.results = None

tab1, tab2 = st.tabs([" Analiz", " Dashboard"])

with tab1:
    # --- Upload bölümü ---
    with st.container(border=True):
        st.subheader("1) Raporu Yükle")
        uploaded = st.file_uploader(
            "PDF/DOCX yükle", 
            type=["pdf", "docx", "doc"], 
            accept_multiple_files=False
        )
        preview = st.checkbox("PDF önizleme (pdf.js viewer)", value=True)
        analyze_btn = st.button("Yükle ve Analiz Et", type="primary")

        # PDF önizleme (tam uyumlu pdf.js viewer)
        if uploaded and preview:
            if uploaded.type == "application/pdf":
                pdf_bytes = uploaded.read()
                st.markdown('<div class="viewer-title">Önizleme</div>', unsafe_allow_html=True)
                pdf_viewer(pdf_bytes, width=900, height=800)  # ✅ hiçbir tarayıcı engellemez
                uploaded.seek(0)
            else:
                st.info("PDF önizleme sadece .pdf dosyaları için aktiftir.")

        # Analiz tetikleme + validasyon
        if analyze_btn:
            if not uploaded:
                st.error("Lütfen PDF/DOCX dosyası yükleyin.")
            elif uploaded.size and uploaded.size > 15 * 1024 * 1024:
                st.error("Dosya 15MB’ı aşıyor. Lütfen daha küçük bir dosya deneyin.")
            else:
                with st.status("Analiz başlatıldı...", expanded=False) as status:
                    st.write("Dosya alındı:", uploaded.name)
                    for pct in range(0, 101, 20):
                        st.progress(pct)
                        time.sleep(0.2)
                    result = run_mock_analysis(None)  # mock analiz
                    st.session_state.results = to_dict(result)
                    st.session_state.job_done = True
                    status.update(label="Analiz tamamlandı ", state="complete")

    # --- Sonuçlar ---
    with st.container(border=True):
        st.subheader("2) Sonuçlar")
        data = st.session_state.get("results")

        if not st.session_state.get("job_done"):
            st.info("Henüz sonuç yok. Dosyayı yükleyip **Analiz Et** butonuna bas.")
        elif not data or not data.get("sections"):
            st.warning("Analiz tamamlandı ama bölüm verisi boş görünüyor.")
        else:
            df = pd.DataFrame(data["sections"])

            def score_chip(s: float) -> str:
                color = "#16a34a" if s >= 8 else "#eab308" if s >= 7 else "#ef4444"
                return f"<span style='background:{color}22;color:{color};padding:4px 8px;border-radius:10px;font-weight:600;'>{s}</span>"

            colA, colB, colC = st.columns([2, 2, 1])
            with colA:
                sort_by = st.selectbox("Sırala", ["name", "score"], index=1)
            with colB:
                asc = st.toggle("Artan sırala", value=False)
            with colC:
                 if data.get("total"):
                    st.metric("Toplam Ortalama", data["total"])

            df_sorted = df.sort_values(by=sort_by, ascending=asc, ignore_index=True)

            for _, row in df_sorted.iterrows():
                with st.expander(f" {row['name']} — skor: {row['score']}"):
                    st.markdown(f"Skor: {score_chip(row['score'])}", unsafe_allow_html=True)
                    st.markdown(f"**Kanıt (alıntı):**\n\n> {row['evidence']}")
                    st.markdown(f"**Öneri:** {row['suggestion']}")

            st.markdown("—")
            st.caption("Tablo görünümü")
            st.dataframe(df_sorted, use_container_width=True, hide_index=True)
            st.download_button(
                "CSV indir",
                df_sorted.to_csv(index=False).encode("utf-8"),
                "results.csv",
                "text/csv"
            )

with tab2:
    st.subheader("Basit Metrikler (Demo)")
    data = st.session_state.get("results")
    if not data:
        st.info("Önce Analiz sekmesinde bir çalıştırma yap.")
    else:
        df = pd.DataFrame(data["sections"])
        st.bar_chart(df.set_index("name")["score"])
        st.write("Rubrik kapsamı:", ", ".join(df["name"].tolist()))
