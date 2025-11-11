# 🚨 ÖNCELİKLİ HAZIRLIKLAR - Görevler Öncesi

## 📊 Durum Özeti

Görevlere başlamadan **ÖNCE** yapılması gereken kritik hazırlıklar:

---

## 1️⃣ VERİ YAPISI (EN ÖNCE YAPILMALI) ⚠️

### Mevcut Durum
- ❌ Sadece `data/sample_reports/` var
- ❌ 150 rapor için organize yapı yok
- ❌ Train/test ayrımı yok

### Neden Önemli?
- 150 raporu düzenli işlemek için klasör yapısı şart
- Metadata.json dosyalarını nereye koyacağınız buna bağlı
- Pipeline test'i bu yapıya göre yazılacak

### Yapılacaklar
```bash
data/
├── raw/              # Ham PDF/DOCX dosyaları (150 rapor)
│   ├── report_001.pdf
│   ├── report_002.pdf
│   └── ...
├── processed/        # İşlenmiş veriler
│   ├── texts/        # Çıkarılmış metinler
│   ├── segmentations/ # Bölümleme çıktıları
│   └── metadata/     # Metadata JSON dosyaları
├── train/            # Eğitim seti (120 rapor)
│   └── (raw'dan kopyalanacak)
└── test/             # Test seti (30 rapor)
    └── (raw'dan kopyalanacak)
```

### Öncelik: ⭐⭐⭐⭐⭐ (EN YÜKSEK)

---

## 2️⃣ METADATA ŞEMASI (2. SIRADA) ⚠️

### Mevcut Durum
- ❌ metadata.json şeması yok
- ✅ Sadece `source_metadata` var segmentation çıktılarında
- ❌ Puan, kriterler bilgisi yok

### Neden Önemli?
- Her rapor için puan ve kriterler saklanmalı
- Train/test ayrımı için metadata gerekli
- Pipeline test'i metadata'ya göre çalışacak

### Yapılacaklar
- `schemas/metadata.schema.json` oluştur
- Alanlar: `report_id`, `filename`, `scores`, `criteria`, `timestamp`, `hash`
- Örnek metadata.json dosyası

### Öncelik: ⭐⭐⭐⭐ (ÇOK YÜKSEK)

---

## 3️⃣ ANONİMLEŞTİRME PLANI (3. SIRADA) ⚠️

### Mevcut Durum
- ❌ Anonimleştirme yok
- ⚠️ SystemSpec'te "gelecek hafta" yazıyor
- ❌ GDPR/KVKK uyumluluğu yok

### Neden Önemli?
- **YASAL GEREKLİLİK** (GDPR/KVKK)
- Kişisel veriler (isim, email, telefon) korunmalı
- Pipeline test'ten önce anonimleştirme olmalı

### Yapılacaklar
- `docs/anonymization_plan.md` oluştur
- Regex pattern'leri tanımla (isim, email, telefon, adres)
- Entity masking stratejisi
- Test scripti

### Öncelik: ⭐⭐⭐⭐⭐ (YASAL GEREKLİLİK)

---

## 4️⃣ .GITIGNORE DOSYASI (4. SIRADA) ⚠️

### Mevcut Durum
- ❌ .gitignore dosyası yok
- ⚠️ Kişisel veriler commit edilebilir (RİSK!)

### Neden Önemli?
- PDF/DOCX dosyaları Git'e commit edilmemeli
- API key'ler korunmalı
- Metadata.json dosyaları (puan bilgisi içeriyor)

### Yapılacaklar
```gitignore
# Kişisel veriler
*.pdf
*.docx
*.doc
data/raw/**
data/train/**
data/test/**

# Metadata (puan bilgisi içeriyor)
data/processed/metadata/**

# API Keys
.env
*.key
*.pem

# Python
__pycache__/
*.pyc
*.pyo
```

### Öncelik: ⭐⭐⭐⭐ (GÜVENLİK)

---

## 5️⃣ PIPELINE TEST SCRIPTI (5. SIRADA)

### Mevcut Durum
- ✅ Tek dosya için script var (`run_segmentation.py`)
- ❌ Batch processing yok
- ❌ Error handling yetersiz

### Neden Önemli?
- 150 raporu toplu işlemek için gerekli
- Mock 3 raporla test için hazır olmalı

### Yapılacaklar
- Batch processing scripti
- Progress tracking
- Error handling ve retry
- Log sistemi

### Öncelik: ⭐⭐⭐ (ORTA)

---

## 📋 ÖNERİLEN ÇALIŞMA SIRASI

```
1. .gitignore dosyası oluştur (5 dakika)
   ↓
2. Veri yapısını oluştur (15 dakika)
   ├── data/raw/
   ├── data/processed/
   ├── data/train/
   └── data/test/
   ↓
3. Metadata şemasını tanımla (30 dakika)
   ├── schemas/metadata.schema.json
   └── Örnek metadata.json
   ↓
4. Anonimleştirme planını oluştur (1 saat)
   ├── docs/anonymization_plan.md
   └── Regex pattern'leri
   ↓
5. Pipeline test scripti hazırla (1 saat)
   └── Batch processing
   ↓
6. Görevlere başla ✅
```

---

## ⚠️ KRİTİK UYARILAR

### 1. Veri Güvenliği
- ❌ **ASLA** PDF/DOCX dosyalarını Git'e commit etmeyin
- ❌ **ASLA** API key'leri commit etmeyin
- ✅ `.gitignore` dosyasını ilk yapın

### 2. Yasal Uyumluluk
- ⚠️ GDPR/KVKK için anonimleştirme **ZORUNLU**
- ⚠️ Kişisel veriler (isim, email) korunmalı
- ✅ Anonimleştirme planını görevlerden önce hazırlayın

### 3. Veri Yapısı
- ✅ Klasör yapısını tutarlı tutun
- ✅ Dosya adlandırma standardı oluşturun
- ✅ README.md dosyaları ekleyin

---

## ✅ HAZIR OLMA KRİTERLERİ

Görevlere başlamadan önce şunlar **MUTLAKA** hazır olmalı:

- [x] `.gitignore` dosyası var ve güncel
- [ ] `data/raw/`, `data/processed/`, `data/train/`, `data/test/` klasörleri var
- [ ] `metadata.json` şeması tanımlı
- [ ] Anonimleştirme planı hazır
- [ ] Pipeline test scripti hazır (en azından taslak)

---

## 🎯 HEMEN YAPILACAKLAR

1. **.gitignore dosyası oluştur** (5 dakika)
2. **Veri yapısını oluştur** (15 dakika)
3. **Metadata şemasını tanımla** (30 dakika)

Bu 3 adım tamamlandıktan sonra görevlere başlayabilirsiniz.

---

## 📞 SORULAR?

Bu hazırlıkları yaparken sorunuz olursa:
- Veri yapısı: `data/` klasörü yapısına bakın
- Metadata: `schemas/` klasöründeki örnek şemalara bakın
- Anonimleştirme: GDPR/KVKK gereksinimlerine bakın

