# 🧾 Bitirme • Python-Only Frontend (Streamlit)

Bu proje, **Bitirme Projesi – Rapor Değerlendirme Sistemi** için yalnızca **Python (Streamlit)** tabanlı frontend uygulamasıdır.  
Backend henüz bağlanmamıştır; analiz çıktıları **mock** olarak üretilir.  
To-Do dokümanındaki **Upload → Analiz Durumu → Sonuç Tablosu** akışını birebir karşılar.

---

## ⚙️ Kurulum (Lokal)

```bash
# 1) Sanal ortam oluştur
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 2) Bağımlılıkları yükle
pip install -r requirements.txt

# 3) Uygulamayı başlat
streamlit run app.py
# Tarayıcı: http://localhost:8501
```

---

## 🐳 Docker ile Çalıştırma

```bash
# 1) Proje klasörüne gir
cd bitirme-frontend

# 2) Build + run
docker compose up -d --build

# 3) Tarayıcıda aç
http://localhost:8501
```

### Canlı düzenleme
`docker-compose.yml` içindeki  
```yaml
volumes:
  - .:/app
```  
satırı sayesinde, dosyalarda yaptığın değişiklikler **otomatik olarak container içinde yansır** (Streamlit auto-reload aktiftir).

### Yayın / Prod
```bash
docker build -t bitirme-fe .
docker run -p 8501:8501 bitirme-fe
```

---

## 🚀 Özellikler

- **Dosya Yükleme (PDF/DOCX)**  
- **PDF Önizleme (pdf.js tabanlı, Chrome engeli yok)**  
- **Analiz Durumu & Progress Bar (mock)**  
- **Sonuç Tablosu** — bölüm, puan, kanıt, öneri + CSV indirme  
- **Dashboard Sekmesi** — ortalama skor ve rubrik kapsamı  
- **Tam Docker Desteği**  

---

## 🧩 Yapı

```
📦 bitirme-frontend
│
├── app.py              # Ana Streamlit uygulaması
├── requirements.txt     # Bağımlılıklar
├── src/
│   ├── analyze.py       # Mock analiz (örnek skor üretimi)
│   └── utils.py         # Yardımcı PDF fonksiyonları
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ✅ To-Do Uyumlu Aşamalar

| Hafta | Hedef | Durum |
|-------|--------|--------|
| 1–2 | Upload + Progress + Tablo (Mock) | ✅ Tamam |
| 3 | Gerçek backend entegrasyonu | ⏳ Beklemede |
| 4 | Puanlama detay paneli + görselleştirme | 🔜 Planlı |
| 5+ | RAG örnek karşılaştırma & kalibrasyon | 🔜 Planlı |

---

## 🧠 Notlar

- PDF önizleme **`streamlit-pdf-viewer`** bileşeniyle yapılır, tarayıcı engeline takılmaz.  
- Maksimum dosya boyutu: **15 MB**  
- Docker ortamında tüm ekip üyeleri aynı sürümle çalışır.  
- Backend bağlandığında yalnızca `run_mock_analysis()` fonksiyonu değiştirilecektir.

---

🎓 **Bitirme Projesi – Rapor Değerlendirme Uygulaması (Frontend)**  
**Enes Ertuğrul • Helin • Ömer • Umut**
