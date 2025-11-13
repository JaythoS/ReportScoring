# Proje Yapısı

## Genel Bakış

Bu proje staj raporlarını otomatik olarak notlandırmak için modüler bir yapı kullanır.

## Klasör Yapısı

```
ReportScoring/
├── core/                          # Ana işlevsel modüller
│   ├── anonymization/             # Anonimleştirme modülü
│   │   ├── __init__.py
│   │   └── anonymizer.py          # Anonimleştirme fonksiyonları
│   ├── scoring/                   # Notlandırma modülü
│   │   ├── __init__.py
│   │   └── segment_scoring.py     # LLM ile puanlama
│   ├── segmentation/               # Segmentasyon modülü
│   │   ├── __init__.py
│   │   ├── segmenter.py           # LLM ile segmentasyon
│   │   └── fix_segmentation.py    # Segmentasyon düzeltme
│   └── extraction/                # Metin çıkarma modülü
│       ├── __init__.py
│       └── pdf_extractor.py       # PDF/DOCX extraction
│
├── llm/                           # LLM işlemleri
│   ├── prompts/                   # Prompt şablonları
│   │   ├── cover_scoring.json.txt
│   │   ├── executive_scoring.json.txt
│   │   └── segmentation.json.txt
│   ├── tools/                     # LLM araçları (eski, migration edilecek)
│   └── docs/                      # LLM dokümantasyonu
│
├── scripts/                       # CLI Scriptleri
│   ├── anonymization/            # Anonimleştirme scriptleri
│   ├── scoring/                   # Scoring scriptleri
│   │   ├── score_cover.py
│   │   ├── score_executive.py
│   │   ├── test_with_real_scores.py
│   │   └── common.py
│   ├── segmentation/              # Segmentasyon scriptleri
│   └── pipeline/                 # Pipeline scriptleri
│
├── data/                          # Veri klasörü
│   ├── raw/                       # Ham raporlar
│   ├── processed/                 # İşlenmiş veriler
│   │   ├── texts/                 # Çıkarılmış metinler
│   │   ├── anonymized/            # Anonimleştirilmiş metinler
│   │   ├── segmentations/         # Segmentasyon çıktıları
│   │   └── anonymization_mappings/ # Anonimleştirme mapping'leri
│   ├── sample_reports/            # Örnek raporlar
│   └── ie_drive/                  # Gerçek notlar (Excel)
│
├── outputs/                       # Çıktılar
│   ├── segmentations/             # Segmentasyon sonuçları
│   ├── cover_scores/              # Cover notlandırma sonuçları
│   └── executive_scores/          # Executive Summary notlandırma sonuçları
│
├── tests/                         # Testler
├── docs/                          # Dokümantasyon
└── schemas/                       # JSON şemaları
```

## Modül Açıklamaları

### Core Modüller

#### `core/extraction/`
PDF ve DOCX dosyalarından metin çıkarma.

**Kullanım:**
```python
from core.extraction import extract_text_from_pdf, extract_text_from_docx

text = extract_text_from_pdf("rapor.pdf")
```

#### `core/segmentation/`
Raporları rubrik bölümlerine ayırma.

**Kullanım:**
```python
from core.segmentation import segment_text_chunked, fix_segmentation

segmentation_json = segment_text_chunked(text)
fixed_data = fix_segmentation(seg_file, text)
```

#### `core/scoring/`
Rubrik kriterlerine göre LLM ile puanlama.

**Kullanım:**
```python
from core.scoring import score_cover_segment, score_executive_summary

cover_score = score_cover_segment(cover_segment)
executive_score = score_executive_summary(executive_segment)
```

#### `core/anonymization/`
GDPR/KVKK uyumluluğu için anonimleştirme.

**Kullanım:**
```python
from core.anonymization import anonymize_file

mapping = anonymize_file(
    input_path="rapor.txt",
    output_path="rapor_anonymized.txt",
    mapping_path="mapping.json"
)
```

## Scripts

### Scoring Scripts
- `scripts/scoring/score_cover.py` - Cover notlandırma
- `scripts/scoring/score_executive.py` - Executive Summary notlandırma
- `scripts/scoring/test_with_real_scores.py` - Gerçek notlarla test

### Pipeline Scripts
- `scripts/pipeline/run_pipeline.py` - Tam pipeline (extraction → segmentation → scoring)

## Veri Akışı

```
PDF/DOCX
  ↓
[Extraction] → Metin
  ↓
[Anonymization] → Anonimleştirilmiş Metin (opsiyonel)
  ↓
[Segmentation] → JSON Segmentasyon
  ↓
[Scoring] → Notlandırma Sonuçları
  ↓
Outputs/
```

## Migration Notları

Eski yapıdan yeni yapıya geçiş:
- `llm/tools/` → `core/` modülleri
- `src/analyze/` → `core/scoring/`
- `scripts/anonymize.py` → `core/anonymization/`

Eski import'lar hala çalışıyor (backward compatibility için), ancak yeni kod `core/` modüllerini kullanmalı.

