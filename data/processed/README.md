# 📁 Processed Data - İşlenmiş Veriler

## 🎯 Amaç

Bu klasör, ham raporlardan çıkarılan ve işlenmiş verileri içerir.

## 📂 Klasör Yapısı

```
processed/
├── texts/              # Çıkarılmış metinler (.txt)
├── segmentations/      # Bölümleme çıktıları (.json)
└── metadata/           # Metadata JSON dosyaları
```

## 📋 Alt Klasörler

### 1. `texts/` - Çıkarılmış Metinler

- **Format:** `.txt` (UTF-8 encoding)
- **Dosya Adı:** `report_XXX.txt`
- **İçerik:** PDF/DOCX'ten çıkarılmış düz metin
- **Kaynak:** `llm/tools/pdf_extractor.py`

### 2. `segmentations/` - Bölümleme Çıktıları

- **Format:** `.json` (UTF-8 encoding)
- **Dosya Adı:** `report_XXX_segmentation.json`
- **İçerik:** Rubric'e göre bölümlenmiş yapı
- **Şema:** `llm/schemas/section.schema.json`
- **Kaynak:** `llm/tools/run_segmentation.py`

### 3. `metadata/` - Metadata Dosyaları

- **Format:** `.json` (UTF-8 encoding)
- **Dosya Adı:** `report_XXX_metadata.json`
- **İçerik:** Rapor metadata'sı (ID, puan, kriterler, tarih)
- **Şema:** `schemas/metadata.schema.json` (oluşturulacak)

## 🔄 İşlem Akışı

```
Raw PDF/DOCX
    ↓
[Metin Çıkarma]
    ↓
processed/texts/report_XXX.txt
    ↓
[Bölümleme (Segmentation)]
    ↓
processed/segmentations/report_XXX_segmentation.json
    ↓
[Metadata Oluşturma]
    ↓
processed/metadata/report_XXX_metadata.json
```

## 📊 Dosya Örnekleri

### Metin Dosyası (`texts/report_001.txt`)
```
Executive Summary
Core4Basis Technology and Consulting Services is a consulting boutique...
[Metin içeriği]
```

### Segmentation Dosyası (`segmentations/report_001_segmentation.json`)
```json
{
  "segmentation": {
    "sections": [
      {
        "section_id": "executive_summary_1",
        "section_name": "Executive Summary",
        "content": "...",
        "start_idx": 0,
        "end_idx": 500,
        "level": 1,
        "parent_id": null
      }
    ]
  },
  "source_metadata": {
    "total_length": 5000,
    "extraction_timestamp": "2024-11-06T10:00:00Z"
  }
}
```

### Metadata Dosyası (`metadata/report_001_metadata.json`)
```json
{
  "report_id": "report_001",
  "filename": "report_001.pdf",
  "scores": {
    "total": 85.5,
    "sections": {
      "executive_summary": 8.5,
      "company_sector": 8.0,
      "activity_analysis": 40.0,
      "conclusion": 6.0
    }
  },
  "criteria": {...},
  "timestamp": "2024-11-06T10:00:00Z",
  "hash": "sha256:..."
}
```

## ⚠️ Önemli Notlar

1. **Git Ignore:** `metadata/` klasörü `.gitignore`'da olmalı (puan bilgisi içerir)
2. **Versiyonlama:** İşlenmiş dosyalar versiyonlanmalı
3. **Yedekleme:** İşlenmiş veriler yedeklenmeli
4. **Tutarlılık:** Her rapor için 3 dosya olmalı (text, segmentation, metadata)

## 🔗 İlgili Dosyalar

- Metin çıkarma: `llm/tools/pdf_extractor.py`
- Bölümleme: `llm/tools/run_segmentation.py`
- Metadata şeması: `schemas/metadata.schema.json` (oluşturulacak)

