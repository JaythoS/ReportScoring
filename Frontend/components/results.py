import streamlit as st
import pandas as pd


def render_results():
    # Analiz yapılmamışsa
    if "results" not in st.session_state or not st.session_state.get("job_done", False):
        st.write("Henüz analiz yapılmadı.")
        return

    data = st.session_state["results"]
    sections = data.get("sections", [])

    if not sections:
        st.write("Bölüm verisi bulunamadı.")
        return

    # Rol: admin / teacher → PUAN GÖRÜR, student → sadece feedback
    role = st.session_state.get("user_role", "student")
    privileged_roles = {"admin", "teacher"}

    # Notlar 5 üzerinden, final not = toplam
    total_score = data.get("total", 0)
    max_total = len(sections) * 5 if sections else 0

    # Sadece admin / teacher’a final not ve progress bar göster
    if role in privileged_roles and max_total > 0:
        st.subheader("Final Not")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.metric("Final Not", f"{total_score} / {max_total}")
        with col2:
            pct = int((total_score / max_total) * 100)
            st.progress(pct, text=f"Genel Uyum: %{pct}")

    # Bölüm bazlı tablo hazırlığı
    df = pd.DataFrame(sections)
    df["kisa_feedback"] = df["suggestion"].apply(
        lambda s: s[:140] + "…" if len(str(s)) > 140 else s
    )

    # Sıralama kontrolleri
    colA, colB = st.columns([2, 2])
    with colA:
        sort_by = st.selectbox("Sırala", ["name", "score"], index=0)
    with colB:
        asc = st.checkbox("Artan", value=False)

    df_sorted = df.sort_values(by=sort_by, ascending=asc, ignore_index=True)

    # Tablo: admin/teacher → skor + feedback, student → sadece feedback
    if role in privileged_roles:
        st.subheader("Bölüm Bazlı Puanlar ve Feedback")
        st.dataframe(
            df_sorted[["name", "score", "kisa_feedback"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.subheader("Bölüm Bazlı Feedback")
        st.dataframe(
            df_sorted[["name", "kisa_feedback"]],
            use_container_width=True,
            hide_index=True,
        )

    # Özet yazı
    try:
        best = df.sort_values(by="score", ascending=False).iloc[0]
        worst = df.sort_values(by="score", ascending=True).iloc[0]

        if role in privileged_roles:
            summary = (
                f"En iyi bölüm: {best['name']} ({best['score']}/5) | "
                f"Gelişime açık bölüm: {worst['name']} ({worst['score']}/5) | "
                f"Öneri: {worst['suggestion']}"
            )
        else:
            summary = (
                f"En güçlü bölüm: {best['name']} | "
                f"Gelişime açık bölüm: {worst['name']} | "
                f"Öneri: {worst['suggestion']}"
            )
    except Exception:
        summary = "Özet oluşturulamadı."

    st.write(summary)

    # CSV export sadece admin / teacher için
    if role in privileged_roles:
        st.download_button(
            label="CSV İndir",
            data=df_sorted.to_csv(index=False).encode("utf-8"),
            file_name="sonuclar.csv",
            mime="text/csv",
        )
