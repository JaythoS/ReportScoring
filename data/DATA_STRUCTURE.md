# 📊 Veri Yapısı Detay Dokümantasyonu

## 🎯 Genel Bakış

Bu dokümantasyon, 150 staj raporu için organize edilmiş veri yapısını detaylı olarak açıklar.

## 📂 Tam Klasör Yapısı

```
data/
├── README.md                    # Ana README
├── DATA_STRUCTURE.md            # Bu dosya
│
├── raw/                         # Ham PDF/DOCX dosyaları (150 rapor)
│   ├── README.md
│   ├── .gitkeep
│   ├── report_001.pdf
│   ├── report_002.pdf
│   ├── ...
│   └── report_150.pdf
│
├── processed/                   # İşlenmiş veriler
│   ├── README.md
│   │
│   ├── texts/                   # Çıkarılmış metinler
│   │   ├── .gitkeep
│   │   ├── report_001.txt
│   │   ├── report_002.txt
│   │   └── ...
│   │
│   ├── segmentations/           # Bölümleme çıktıları
│   │   ├── .gitkeep
│   │   ├── report_001_segmentation.json
│   │   ├── report_002_segmentation.json
│   │   └── ...
│   │
│   └── metadata/                # Metadata JSON dosyaları
│       ├── .gitkeep
│       ├── report_001_metadata.json
│       ├── report_002_metadata.json
│       └── ...
│
├── train/                       # Eğitim seti (120 rapor)
│   ├── README.md
│   ├── .gitkeep
│   ├── report_001.pdf
│   ├── report_002.pdf
│   └── ...
│
├── test/                        # Test seti (30 rapor)
│   ├── README.md
│   ├── .gitkeep
│   ├── report_121.pdf
│   ├── report_122.pdf
│   └── ...
│
└── sample_reports/              # Örnek raporlar (test için)
    ├── README.md
    └── [örnek PDF'ler]
```

## 📋 Dosya Adlandırma Standardı

### 1. Raw Dosyalar
- **Format:** `report_XXX.pdf` veya `report_XXX.docx`
- **XXX:** 3 haneli sıra numarası (001, 002, ..., 150)
- **Örnekler:**
  - `report_001.pdf`
  - `report_042.docx`
  - `report_150.pdf`

### 2. İşlenmiş Metinler
- **Format:** `report_XXX.txt`
- **Encoding:** UTF-8
- **Örnekler:**
  - `report_001.txt`
  - `report_042.txt`

### 3. Bölümleme Çıktıları
- **Format:** `report_XXX_segmentation.json`
- **Encoding:** UTF-8
- **Örnekler:**
  - `report_001_segmentation.json`
  - `report_042_segmentation.json`

### 4. Metadata Dosyaları
- **Format:** `report_XXX_metadata.json`
- **Encoding:** UTF-8
- **Örnekler:**
  - `report_001_metadata.json`
  - `report_042_metadata.json`

## 🔄 İşlem Akışı

### Adım 1: Ham Rapor Yükleme
```
Kullanıcı → data/raw/report_001.pdf
```

### Adım 2: Metin Çıkarma
```
data/raw/report_001.pdf
    ↓ [pdf_extractor.py]
data/processed/texts/report_001.txt
```

### Adım 3: Bölümleme (Segmentation)
```
data/processed/texts/report_001.txt
    ↓ [run_segmentation.py]
data/processed/segmentations/report_001_segmentation.json
```

### Adım 4: Metadata Oluşturma
```
data/processed/segmentations/report_001_segmentation.json
    ↓ [metadata_generator.py]
data/processed/metadata/report_001_metadata.json
```

### Adım 5: Train/Test Ayrımı
```
data/raw/ (150 rapor)
    ↓ [split_data.py]
data/train/ (120 rapor)
data/test/ (30 rapor)
```

## 📊 Train/Test Dağılımı

### İstatistikler
- **Toplam:** 150 rapor
- **Train:** 120 rapor (%80)
- **Test:** 30 rapor (%20)

### Ayrım Stratejisi

**Seçenek 1: Sıralı Ayrım**
```python
train = report_001 ... report_120
test = report_121 ... report_150
```

**Seçenek 2: Rastgele Ayrım (Önerilen)**
```python
import random
reports = list(range(1, 151))
random.shuffle(reports)
train = reports[:120]
test = reports[120:]
```

### Ayrım Bilgisi
Ayrım bilgisi `data/split_info.json` dosyasına kaydedilir:
```json
{
  "train": ["report_001", "report_042", ...],
  "test": ["report_121", "report_150", ...],
  "split_date": "2024-11-06T10:00:00Z",
  "split_method": "random"
}
```

## 🔒 Güvenlik ve Git

### Git Ignore Kuralları
- ✅ `data/raw/**` - Kişisel veriler içerir
- ✅ `data/train/**` - Kişisel veriler içerir
- ✅ `data/test/**` - Kişisel veriler içerir
- ✅ `data/processed/metadata/**` - Puan bilgisi içerir
- ✅ `*.pdf`, `*.docx` - Ham dosyalar

### Commit Edilebilir Dosyalar
- ✅ README.md dosyaları
- ✅ `.gitkeep` dosyaları
- ✅ İşlenmiş metinler (opsiyonel)
- ✅ Bölümleme çıktıları (opsiyonel)

## 📈 Versiyonlama

### Dosya Versiyonlama
İşlenmiş dosyalar versiyonlanabilir:
- `report_001_segmentation_v1.json`
- `report_001_segmentation_v2.json`

### Metadata Versiyonlama
```json
{
  "report_id": "report_001",
  "version": "v1",
  "processing_date": "2024-11-06T10:00:00Z",
  ...
}
```

## 🔗 İlgili Dosyalar

### Scriptler
- Metin çıkarma: `llm/tools/pdf_extractor.py`
- Bölümleme: `llm/tools/run_segmentation.py`
- Metadata oluşturma: `scripts/generate_metadata.py` (oluşturulacak)
- Train/Test ayrımı: `scripts/split_data.py` (oluşturulacak)

### Şemalar
- Bölümleme şeması: `llm/schemas/section.schema.json`
- Metadata şeması: `schemas/metadata.schema.json` (oluşturulacak)

### Dokümantasyon
- Ana README: `data/README.md`
- Raw README: `data/raw/README.md`
- Processed README: `data/processed/README.md`
- Train README: `data/train/README.md`
- Test README: `data/test/README.md`

## ✅ Kontrol Listesi

Veri yapısının hazır olduğunu doğrulamak için:

- [ ] Tüm klasörler oluşturuldu
- [ ] README.md dosyaları eklendi
- [ ] .gitkeep dosyaları eklendi
- [ ] .gitignore dosyası güncellendi
- [ ] Dosya adlandırma standardı belirlendi
- [ ] Train/Test ayrımı stratejisi belirlendi
- [ ] İşlem akışı dokümante edildi

## 🎯 Sonraki Adımlar

1. ✅ Veri yapısı oluşturuldu
2. ⏭️ Metadata şeması tanımlanacak
3. ⏭️ Anonimleştirme planı hazırlanacak
4. ⏭️ Pipeline test scripti hazırlanacak
5. ⏭️ Mock 3 raporla test edilecek

