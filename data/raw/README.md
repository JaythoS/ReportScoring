# 📁 Raw Data - Ham Raporlar

## 🎯 Amaç

Bu klasör, işlenmemiş ham PDF/DOCX staj raporlarını içerir.

## 📋 İçerik

- **Toplam Rapor Sayısı:** 150
- **Formatlar:** PDF (.pdf), DOCX (.docx)
- **Dosya Adlandırma:** `report_XXX.pdf` veya `report_XXX.docx`
  - XXX: 3 haneli sıra numarası (001, 002, ..., 150)

## 📂 Klasör Yapısı

```
raw/
├── report_001.pdf
├── report_002.pdf
├── report_003.docx
├── ...
└── report_150.pdf
```

## ⚠️ Önemli Notlar

1. **Git Ignore:** Bu klasör `.gitignore`'da olmalı (kişisel veriler içerir)
2. **Değiştirilmez:** Raw dosyalar ASLA değiştirilmemeli
3. **Yedekleme:** Dosyalar yedeklenmeli (Git'e commit edilmemeli)
4. **Orijinal:** Sadece orijinal PDF/DOCX dosyaları burada olmalı

## 🔄 İşlem Akışı

1. Raporlar bu klasöre yüklenir
2. Dosyalar `report_XXX.pdf` formatında adlandırılır
3. İşleme scripti bu klasörü okur
4. İşlenmiş çıktılar `processed/` klasörüne kaydedilir

## 📊 Rapor Özellikleri

- **Dil:** Türkçe veya İngilizce
- **Format:** PDF veya DOCX
- **Boyut:** Maksimum 15 MB (Frontend limiti)
- **İçerik:** Staj raporu (Executive Summary, Company, Activities, Conclusion)

## 🔗 İlgili Klasörler

- İşlenmiş metinler: `../processed/texts/`
- Bölümlemeler: `../processed/segmentations/`
- Metadata: `../processed/metadata/`

