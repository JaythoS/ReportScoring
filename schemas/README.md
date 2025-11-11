# 📋 Schemas Klasörü - Metadata Şeması

## 🎯 Genel Bakış

Bu klasör, staj raporu metadata şemasını ve örnek dosyalarını içerir.

## 📁 Dosyalar

### 1. `metadata.schema.json` - Metadata JSON Schema

**Ne işe yarar?**
- Metadata JSON dosyalarının yapısını tanımlar
- Veri doğrulama (validation) için kullanılır
- Hangi alanların zorunlu, hangilerinin opsiyonel olduğunu belirtir
- Her alanın tipini ve kısıtlamalarını tanımlar

**Ana Alanlar:**
- `report_id`: Benzersiz rapor tanımlayıcısı (report_001, report_042, ...)
- `filename`: Orijinal dosya adı
- `scores`: Puanlar (total, sections)
- `criteria`: Rubric kriterleri (her bölüm için detaylı değerlendirme)
- `file_paths`: İlgili dosya yolları
- `processing_info`: İşleme bilgileri
- `file_hash`: Dosya hash'i (doğrulama için)
- `dataset_split`: Veri seti ayrımı (train/test)

**Kullanım Alanları:**
- ✅ Metadata validation (JSON Schema validation)
- ✅ API dokümantasyonu
- ✅ Type hint'ler için referans
- ✅ Metadata generator scripti için şablon

---

### 2. `example_metadata.json` - Örnek Metadata

**Ne işe yarar?**
- Gerçek bir örnek metadata dosyası gösterir
- Tüm alanların nasıl doldurulacağını gösterir
- Testlerde beklenen formatı gösterir
- Geliştiriciler için referans

**İçerik:**
- Rubric'e göre tüm bölümler için puanlar
- Her bölüm için kanıt (evidence) ve öneriler (suggestions)
- Dosya yolları ve işleme bilgileri
- Hash değerleri (doğrulama için)

---

## 📊 Rubric Kriterleri ve Ağırlıklar

Metadata şeması, Internship Grading Rubric 2021'e göre yapılandırılmıştır:

| Bölüm | Ağırlık | Açıklama |
|-------|---------|----------|
| Executive Summary | 6% | Engineering activities, internship activities, learned benefits |
| Company and Sector | 8% | Company info, organization, production/service |
| Professional and Ethical Responsibilities | 8% | Professional and ethical responsibilities (Level 2, Company altında) |
| Activity Analysis / Project | 40% | EN ÖNEMLİ - IE activities, problem detection, improvements |
| Conclusion | 6% | Evaluation of internship activities |
| Impact | 8% | Level 2, Conclusion altında - Global, economic, environmental, societal |
| Team Work | 6% | Level 2, Conclusion altında - Collaboration, communication |
| Self-directed Learning | 8% | Level 2, Conclusion altında - New skills, learning process |
| Format and Organisation | 10% | Cover, contents, references, formatting |

**Toplam:** 100%

---

## 🔧 Kullanım Örnekleri

### 1. Metadata Validation

```python
import json
import jsonschema
from pathlib import Path

# Şemayı yükle
schema_path = Path("schemas/metadata.schema.json")
schema = json.loads(schema_path.read_text())

# Metadata dosyasını yükle
metadata_path = Path("data/processed/metadata/report_001_metadata.json")
metadata = json.loads(metadata_path.read_text())

# Validate et
try:
    jsonschema.validate(instance=metadata, schema=schema)
    print("✅ Metadata geçerli")
except jsonschema.ValidationError as e:
    print(f"❌ Validation hatası: {e}")
```

### 2. Metadata Oluşturma

```python
from datetime import datetime
import json

metadata = {
    "report_id": "report_001",
    "filename": "report_001.pdf",
    "timestamp": datetime.now().isoformat(),
    "version": "v1",
    "scores": {
        "total": 85.5,
        "sections": {
            "executive_summary": 8.5,
            "company_sector": 8.0,
            # ... diğer bölümler
        }
    },
    # ... diğer alanlar
}

# Kaydet
with open("data/processed/metadata/report_001_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
```

### 3. Metadata Okuma

```python
import json
from pathlib import Path

# Metadata dosyasını oku
metadata_path = Path("data/processed/metadata/report_001_metadata.json")
metadata = json.loads(metadata_path.read_text())

# Puanları al
total_score = metadata["scores"]["total"]
activity_score = metadata["scores"]["sections"]["activity_analysis"]

print(f"Toplam puan: {total_score}")
print(f"Activity Analysis puanı: {activity_score}")
```

---

## 📋 Zorunlu Alanlar

Metadata şemasında zorunlu alanlar:
- ✅ `report_id` - Benzersiz rapor ID'si
- ✅ `filename` - Dosya adı
- ✅ `timestamp` - Oluşturulma zamanı
- ✅ `file_paths.raw_file` - Ham dosya yolu

**Not:** Puanlar (`scores`) ve kriterler (`criteria`) henüz puanlama yapılmadıysa boş bırakılabilir.

---

## 🔗 İlgili Dosyalar

- Segmentation şeması: `llm/schemas/section.schema.json`
- Metadata generator: `scripts/generate_metadata.py` (oluşturulacak)
- Validation script: `scripts/validate_metadata.py` (oluşturulacak)

---

## ✅ Kontrol Listesi

- [x] Metadata şeması oluşturuldu
- [x] Örnek metadata dosyası oluşturuldu
- [x] README dokümantasyonu hazır
- [ ] Metadata generator scripti (oluşturulacak)
- [ ] Validation scripti (oluşturulacak)

