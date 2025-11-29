import streamlit as st
import pandas as pd


def render_dashboard(results_data):
    role = st.session_state.get("user_role", "student")

    if role not in ["admin", "teacher"]:
        st.write("Bu alan yalnızca öğretmenler içindir.")
        return

    if not results_data or "sections" not in results_data:
        st.write("Henüz analiz yapılmadı.")
        return

    df = pd.DataFrame(results_data["sections"])

    st.subheader("Puan Dağılımı")
    st.bar_chart(df.set_index("name")["score"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("En Yüksek", df["score"].max())
    with col2:
        st.metric("En Düşük", df["score"].min())
    with col3:
        st.metric("Ortalama", round(df["score"].mean(), 2))

    st.subheader("Tüm Skor Tablosu")
    st.dataframe(
        df[["name", "score"]],
        hide_index=True,
        use_container_width=True
    )
