import streamlit as st
import pandas as pd
from datetime import datetime

def render_history():
    """
    Geçmiş Analizler sekmesini oluşturur.
    Session içinde tutulan analiz geçmişini tablo olarak gösterir.
    """
    st.subheader(" Geçmiş Analizler")

    # Eğer geçmiş yoksa bilgi mesajı
    if "history" not in st.session_state:
        st.session_state["history"] = []

    history_data = st.session_state["history"]

    if len(history_data) == 0:
        st.info("Henüz kayıtlı analiz yok. Bir dosya yükleyip analiz başlatın.")
        return

    # DataFrame'e dönüştür
    df = pd.DataFrame(history_data)

    # Sıralama (tarihine göre yeni → eski)
    if "Tarih" in df.columns:
        df = df.sort_values(by="Tarih", ascending=False)

    # Görsel tablo
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # CSV export (isteğe bağlı)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        " Geçmişi CSV olarak indir",
        csv,
        "gecmis_analizler.csv",
        "text/csv"
    )

def add_to_history(filename: str, total_score: float):
    """
    Yeni analiz kaydını geçmiş listesine ekler.
    """
    if "history" not in st.session_state:
        st.session_state["history"] = []

    st.session_state["history"].append({
        "Dosya Adı": filename,
        "Tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Skor": round(total_score, 2)
    })
