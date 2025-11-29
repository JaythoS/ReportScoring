import streamlit as st
import pandas as pd
from datetime import datetime


def add_to_history(filename, total_score):
    if "history" not in st.session_state:
        st.session_state["history"] = []

    st.session_state["history"].append({
        "Dosya Adı": filename,
        "Tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Final Not": total_score
    })


def render_history():
    role = st.session_state.get("user_role", "student")

    if role not in ["admin", "teacher"]:
        st.write("Bu alan yalnızca öğretmenlere açıktır.")
        return

    st.subheader("Geçmiş Analizler")

    history = st.session_state.get("history", [])

    if not history:
        st.write("Henüz geçmiş analiz bulunmuyor.")
        return

    df = pd.DataFrame(history)

    if "Tarih" in df.columns:
        df = df.sort_values(by="Tarih", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Geçmişi CSV Olarak İndir",
        csv,
        "gecmis_analizler.csv",
        "text/csv"
    )
