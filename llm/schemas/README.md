# Schemas Klasörü Açıklaması

Bu klasör, LLM bölümleme sisteminin çıktı formatını tanımlayan şema dosyalarını içerir.

## 📁 Dosyalar

### 1. `section.schema.json` - JSON Schema Tanımı

**Ne işe yarar?**
- LLM'den gelen JSON çıktısının yapısını tanımlar
- Veri doğrulama (validation) için kullanılır
- Hangi alanların zorunlu, hangilerinin opsiyonel olduğunu belirtir
- Her alanın tipini ve kısıtlamalarını tanımlar

**İçerik:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Staj Raporu Bölümleme Şeması",
  "properties": {
    "segmentation": {
      "sections": [
        {
          "section_id": "string (zorunlu)",
          "section_name": "string (zorunlu)",
          "content": "string (zorunlu)",
          "start_idx": "integer (zorunlu, min: 0)",
          "end_idx": "integer (zorunlu, min: 0)",
          "level": "integer (zorunlu, 1-5 arası)",
          "parent_id": "string veya null (opsiyonel)",
          "page_number": "integer veya null (opsiyonel)"
        }
      ]
    },
    "source_metadata": {
      "total_length": "integer (zorunlu)",
      "extraction_timestamp": "string (zorunlu, ISO 8601)",
      "source_hash": "string (opsiyonel)"
    }
  }
}
```

**Kullanım Alanları:**
- ✅ LLM prompt'una referans (beklenen çıktı formatı)
- ✅ Çıktı doğrulama (validation)
- ✅ API dokümantasyonu
- ✅ Type hint'ler için referans

---

### 2. `example_output.json` - Örnek Çıktı

**Ne işe yarar?**
- Gerçek bir örnek çıktı gösterir
- LLM prompt'unda örnek olarak kullanılır
- Testlerde beklenen formatı gösterir
- Geliştiriciler için referans

**İçerik (Rubric-Based):**
Gerçek bir staj raporunun rubric'e göre bölümlenmiş hali:
- ~17 bölüm örneği (Cover, Executive Summary, Company and Sector, Activity Analysis / Project, Conclusion, References)
- Rubric kriterlerine karşılık gelen tüm bölümler
- Her bölüm için tüm alanlar dolu
- Hiyerarşik yapı örneği (Level 1, Level 2)
- parent_id ilişkisi örneği (Impact, Team Work, Self-directed Learning → Level 2, Conclusion altında)

**Örnek Bölüm (Rubric-Based):**
```json
{
  "section_id": "impact_14",
  "section_name": "A) Impact",
  "content": "A) Impact\nMy internship experience gave me insights into...",
  "start_idx": 3651,
  "end_idx": 3900,
  "level": 2,
  "parent_id": "conclusion_13"
}
```

---

## 🔑 Anahtar Alanlar Açıklaması

### `section_id`
- **Tip:** String
- **Örnek:** `"intro_1"`, `"method_1_1"`
- **Amaç:** Bölümü benzersiz olarak tanımlar
- **Kural:** Aynı bölümde tekrar edemez

### `section_name`
- **Tip:** String
- **Örnek:** `"Giriş"`, `"Yöntem"`, `"Kullanılan Teknolojiler"`
- **Amaç:** Bölüm başlığı (orijinal metinden)
- **Kural:** Faithful extraction - değiştirilmeden

### `content`
- **Tip:** String
- **Amaç:** Bölüm içeriği (tam metin)
- **Kural:** Orijinal metinden kelime kelime, değiştirilmeden

### `start_idx` / `end_idx`
- **Tip:** Integer
- **Amaç:** Kaynak metindeki karakter pozisyonları
- **Kural:** 
  - `start_idx`: Başlangıç (0-based)
  - `end_idx`: Bitiş (exclusive)
  - `end_idx > start_idx` olmalı

### `level`
- **Tip:** Integer (1-5)
- **Amaç:** Hiyerarşik seviye (Rubric'e göre)
- **Kural:**
  - Level 1: Ana bölümler (Cover, Executive Summary, Company and Sector, Activity Analysis / Project, Conclusion)
  - Level 2: Alt bölümler (Professional and Ethical Responsibilities, Impact, Team Work, Self-directed Learning, Daily Activities)
  - Level 3+: Alt-alt bölümler (minimal kullanım)

### `parent_id`
- **Tip:** String veya null
- **Amaç:** Üst bölümün ID'si (Rubric'e göre kritik)
- **Kural:**
  - Level 1 → `null`
  - Level 2+ → Üst bölümün `section_id`
  - **Rubric Kuralı:** Impact, Team Work, Self-directed Learning → MUTLAKA `parent_id = conclusion section_id`
  - **Rubric Kuralı:** Professional and Ethical Responsibilities → MUTLAKA `parent_id = company_sector section_id`
  - **Rubric Kuralı:** Daily Activities → MUTLAKA `parent_id = activity_analysis section_id`

### `page_number`
- **Tip:** Integer veya null
- **Amaç:** PDF'deki sayfa numarası
- **Kural:** Opsiyonel, PDF çıktısında kullanılabilir

---

## 🔄 Şema ve Örnek Arasındaki İlişki

```
section.schema.json (ŞEMA)
    ↓ tanımlar
example_output.json (ÖRNEK)
    ↓ gösterir
LLM Prompt (segmentation.json.txt)
    ↓ kullanır
Gerçek Çıktı (demo_output.xml)
```

**Akış:**
1. Şema → Çıktı formatını tanımlar
2. Örnek → Şemaya uygun bir örnek gösterir
3. Prompt → LLM'e örnek gösterir
4. LLM → Şemaya uygun çıktı üretir

---

## ✅ Şema Uyumu Kontrolü

Şema uyumluluğunu kontrol etmek için:

```python
import json
import jsonschema

# Şema ve çıktıyı yükle
with open('section.schema.json') as f:
    schema = json.load(f)
    
with open('example_output.json') as f:
    output = json.load(f)

# Doğrula
jsonschema.validate(output, schema)
print("✅ Şema uyumlu!")
```

---

## 📝 Notlar

- **JSON Schema Draft 07:** Standart JSON Schema formatı
- **Faithful Extraction:** `content` alanı her zaman orijinal metinden olmalı
- **Hiyerarşi:** `parent_id` ile bölümler arası ilişki kurulur
- **Karakter Pozisyonları:** `start_idx` ve `end_idx` faithful extraction için kritik

---

## 🔗 İlgili Dosyalar

- **Prompt:** `llm/prompts/segmentation.json.txt` (şemayı referans alır)
- **Test:** `llm/tests/test_faithful.py` (şemaya uygunluğu test eder)
- **Dokümantasyon:** `docs/system_spec_llm_segmenter.md` (şema açıklaması)

