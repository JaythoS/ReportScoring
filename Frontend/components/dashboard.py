import streamlit as st
import pandas as pd

def render_dashboard(results_data: dict):
    """
    Dashboard sekmesini çizer.
    Bar chart + en yüksek / en düşük skor metriklerini gösterir.
    """
    st.subheader("Basit Metrikler (Demo)")

    if not results_data or "sections" not in results_data:
        st.info("Önce Analiz sekmesinde bir çalıştırma yap.")
        return

    # Veriyi DataFrame'e dönüştür
    df = pd.DataFrame(results_data["sections"])

    # Skorlar üzerinden bar chart
    c1, c2 = st.columns([2, 1])
    with c1:
        st.bar_chart(df.set_index("name")["score"])

    # Metrikler
    with c2:
        max_score = df["score"].max()
        min_score = df["score"].min()
        avg_score = df["score"].mean()

        st.metric("En Yüksek Skor", f"{max_score:.2f}")
        st.metric("En Düşük Skor", f"{min_score:.2f}")
        st.metric("Ortalama Skor", f"{avg_score:.2f}")

    # Ek olarak tabloyu da isteğe bağlı göster
    with st.expander(" Tüm Skor Tablosu"):
        st.dataframe(df[["name", "score"]], use_container_width=True, hide_index=True)
