# 📁 Veri Yapısı - 150 Rapor İçin Organize Klasör Yapısı

## 🎯 Genel Bakış

Bu klasör yapısı, 150 staj raporunun organize edilmesi ve işlenmesi için tasarlanmıştır.

## 📂 Klasör Yapısı

```
data/
├── raw/                    # Ham PDF/DOCX dosyaları (150 rapor)
│   ├── report_001.pdf
│   ├── report_002.pdf
│   └── ...
│
├── processed/              # İşlenmiş veriler
│   ├── texts/             # Çıkarılmış metinler (.txt)
│   ├── segmentations/     # Bölümleme çıktıları (.json)
│   └── metadata/          # Metadata JSON dosyaları
│
├── train/                  # Eğitim seti (120 rapor)
│   └── (raw'dan kopyalanacak)
│
├── test/                   # Test seti (30 rapor)
│   └── (raw'dan kopyalanacak)
│
└── sample_reports/         # Örnek raporlar (test için)
    └── (mevcut örnekler)
```

## 📋 Dosya Adlandırma Standardı

### Raw Dosyalar
- Format: `report_XXX.pdf` veya `report_XXX.docx`
- XXX: 3 haneli sıra numarası (001, 002, ..., 150)
- Örnek: `report_001.pdf`, `report_042.docx`

### İşlenmiş Dosyalar
- Metinler: `report_XXX.txt`
- Segmentations: `report_XXX_segmentation.json`
- Metadata: `report_XXX_metadata.json`

## 🔄 İşlem Akışı

```
1. Ham Raporlar
   data/raw/report_001.pdf
   ↓
2. Metin Çıkarma
   data/processed/texts/report_001.txt
   ↓
3. Bölümleme (Segmentation)
   data/processed/segmentations/report_001_segmentation.json
   ↓
4. Metadata Oluşturma
   data/processed/metadata/report_001_metadata.json
   ↓
5. Train/Test Ayrımı
   data/train/ veya data/test/
```

## 📊 Train/Test Dağılımı

- **Toplam:** 150 rapor
- **Train:** 120 rapor (%80)
- **Test:** 30 rapor (%20)

### Train/Test Ayrımı Stratejisi
- Rastgele seçim (stratified değil, çünkü puanlar henüz bilinmiyor)
- İlk 120 rapor → Train
- Son 30 rapor → Test
- Veya: Random shuffle sonrası ayrım

## ⚠️ Önemli Notlar

1. **Git İgnore:** `raw/`, `train/`, `test/` klasörleri `.gitignore`'da olmalı
2. **Metadata:** Her rapor için metadata.json dosyası zorunlu
3. **Versiyonlama:** İşlenmiş dosyalar versiyonlanmalı (örn: `report_001_segmentation_v1.json`)
4. **Backup:** Raw dosyalar yedeklenmeli (Git'e commit edilmemeli)

## 🔗 İlgili Dosyalar

- Metadata şeması: `schemas/metadata.schema.json` (oluşturulacak)
- Bölümleme şeması: `llm/schemas/section.schema.json`
- İşleme scripti: `llm/tools/run_segmentation.py`

