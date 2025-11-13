import streamlit as st
import pandas as pd

def render_results():
    """
    Analiz sonuçlarını gösterir:
    - Genel skor kutusu
    - Skor ilerleme çubuğu
    - Bölüm tablosu (feedback dahil)
    - Özet rapor
    - CSV indirme
    """

    st.subheader(" 2) Analiz Sonuçları")

    # Sonuçlar session'da yoksa uyarı
    if "results" not in st.session_state or not st.session_state.get("job_done", False):
        st.info("Henüz analiz yapılmadı. Yukarıdan bir rapor yükleyip **Yükle ve Analiz Et** butonuna basın.")
        return

    data = st.session_state["results"]
    if not data or "sections" not in data:
        st.warning("Analiz tamamlandı ama bölüm verisi boş görünüyor.")
        return

    total_score = data.get("total", 0.0)

    # --- Genel skor + progress ---
    st.markdown("###  Genel Skor")
    c1, c2 = st.columns([1, 5])
    with c1:
        st.metric("Toplam Ortalama", f"{total_score:.2f}")
    with c2:
        st.progress(int((total_score / 10) * 100), text=f"Genel Uyum: %{int((total_score / 10) * 100)}")

    # --- Bölüm tablosu ---
    df = pd.DataFrame(data["sections"])

    # Feedback metinlerini kısalt (uzun metinlerde “…”)
    df["Kısa Geri Bildirim"] = df["suggestion"].apply(lambda s: s[:140] + "…" if len(str(s)) > 140 else s)

    # Sıralama alanları
    colA, colB = st.columns([2, 2])
    with colA:
        sort_by = st.selectbox("Sırala", ["name", "score"], index=1)
    with colB:
        asc = st.toggle("Artan sırala", value=False)

    df_sorted = df.sort_values(by=sort_by, ascending=asc, ignore_index=True)

    # Görsel tablo
    st.markdown("### Bölüm Bazlı Skorlar ve Feedback")
    st.dataframe(
        df_sorted[["name", "score", "Kısa Geri Bildirim"]],
        use_container_width=True,
        hide_index=True
    )

    # --- Özet Rapor ---
    try:
        raw = pd.DataFrame(data["sections"])
        worst = raw.sort_values(by="score", ascending=True).iloc[0]
        best = raw.sort_values(by="score", ascending=False).iloc[0]
        summary_txt = (
            f"**Özet Rapor:** Genel skor {total_score:.2f}. "
            f"En güçlü bölüm: **{best['name']} ({best['score']:.2f})**. "
            f"Geliştirmeye açık bölüm: **{worst['name']} ({worst['score']:.2f})**. "
            f"Kısa öneri: {worst['suggestion']}"
        )
    except Exception:
        summary_txt = "**Özet Rapor:** Genel değerlendirme için yeterli veri bulunamadı."

    st.markdown("---")
    st.markdown(summary_txt)

    # --- CSV indirme ---
    st.download_button(
        label="Sonuçları CSV olarak indir",
        data=df_sorted.to_csv(index=False).encode("utf-8"),
        file_name="analiz_sonuclari.csv",
        mime="text/csv"
    )
