# System Specification v1 - LLM Bölümleyici Modülü

## Genel Bakış

**Modül Adı:** LLM-Based Document Segmentation (Bölümleme)  
**Versiyon:** 2.0 (Rubric-Based)  
**Hedef:** Staj raporlarını notlandırma rubric'ine göre bölümlere ayırma (faithful extraction prensibi ile)  
**Rubric Referansı:** Internship Grading Rubric 2021

---

## Girdi/Çıktı Tanımları

### Girdi (Input)

**Format:** Düz metin (string)
- Kaynak: PDF veya DOCX dosyasından çıkarılmış metin
- Encoding: UTF-8
- Maksimum uzunluk: 50,000 karakter (yaklaşık 10,000 kelime)

**Metadata:**
- Dosya adı
- Sayfa numaraları (opsiyonel)
- Çıkarım zamanı

### Çıktı (Output)

**Format:** XML veya JSON (şemaya uygun)

**Şema:** `llm/schemas/section.schema.json`

**Alanlar:**
- `segmentation.sections[]`: Bölüm dizisi
  - `section_id`: Benzersiz tanımlayıcı
  - `section_name`: Bölüm başlığı (orijinal metinden)
  - `content`: Bölüm içeriği (değiştirilmeden)
  - `start_idx`: Başlangıç karakter pozisyonu (0-based)
  - `end_idx`: Bitiş karakter pozisyonu (exclusive)
  - `level`: Hiyerarşik seviye (1-5)
  - `parent_id`: Üst bölüm ID (opsiyonel)
  - `page_number`: Sayfa numarası (opsiyonel)

**Örnek Çıktı:** `llm/schemas/example_output.json`

---

## Fonksiyonel Gereksinimler

### FR-1: Rubric'e Göre Metin Bölümleme
- **Açıklama:** Staj raporu metnini notlandırma rubric'ine göre bölümlere ayırma
- **Rubric Kriterleri:**
  - **Executive Summary** (6% ağırlık) - Level 1
  - **Overview of the Company and Sector** (8% ağırlık) - Level 1
    - Alt bölümler: a) Overview, b) Organization, c) Production/Service - Level 2
    - **Professional and Ethical Responsibilities** (8% ağırlık) - Level 2 (parent_id = company_sector)
  - **Activity Analysis / Project** (40% ağırlık - EN ÖNEMLİ) - Level 1
    - Alt bölümler: Main List of Activities, Activity Analysis, Project, Daily Activities - Level 2
  - **Conclusion** (6% ağırlık) - Level 1
    - Alt bölümler: Impact (8%), Team Work (6%), Self-directed Learning (8%) - Level 2
  - **Format and Organisation** (10% ağırlık) - Cover, Contents, References yapısal bölümler
- **Kriterler:**
  - Rubric kriterlerine karşılık gelen tüm bölümler tespit edilmeli
  - Hiyerarşi doğru olmalı (Level 1, Level 2 ilişkileri)
  - Başarı oranı: %90+ (ana bölümler için)

### FR-2: Faithful Extraction
- **Açıklama:** Orijinal metni değiştirmeden çıkarım yapma
- **Kriterler:**
  - İçerik %100 orijinal metinden (kelime değişikliği yok)
  - Karakter pozisyonları doğru (±5 karakter tolerans)
  - Hallucination oranı < %5

### FR-3: Structured Output
- **Açıklama:** Şema uyumlu XML/JSON çıktı üretme
- **Kriterler:**
  - Şema validation: %100 başarı
  - Gerekli alanlar: Tümü dolu
  - XML/JSON geçerli format

### FR-4: Hiyerarşi Tespiti
- **Açıklama:** Başlık seviyelerini doğru belirleme
- **Kriterler:**
  - Level 1: Ana bölümler
  - Level 2+: Alt bölümler
  - parent_id ilişkileri doğru

---

## Teknik Gereksinimler

### TR-1: LLM Entegrasyonu
- **Model:** Google Gemini 1.5 Flash (varsayılan)
- **Fallback:** GPT-4o-mini (JSON mode)
- **API Key Yönetimi:** Environment variable (`GEMINI_API_KEY`)

### TR-2: Prompt Mühendisliği (Rubric-Based)
- **Format:** JSON-structured
- **Dosya:** `llm/prompts/segmentation.json.txt`
- **Özellikler:**
  - Rubric kriterlerine göre bölüm yapılandırması
  - Hallucination önleyici direktifler
  - Şema zorunluluğu
  - Faithful extraction vurgusu
  - Kritik hiyerarşi kuralları (Impact, Team Work, Self-directed Learning → Level 2)
  - Birleştirme kuralları (Cover, Executive Summary, Daily Activities birleşik)

### TR-3: Doğrulama (Validation)
- **Şema kontrolü:** JSON Schema veya XML Schema
- **İndeks kontrolü:** Overlap ve gap tespiti
- **İçerik kontrolü:** Orijinal metinle karşılaştırma

### TR-4: Hata Yönetimi
- **Retry mekanizması:** Başarısız isteklerde 1 kez tekrar
- **Hata mesajları:** Kullanıcı dostu, teşhis edilebilir
- **Fallback:** Model değiştirme (Gemini → GPT)

---

## Performans Gereksinimleri

### PR-1: Yanıt Süresi
- **Hedef:** < 5 saniye (ortalama)
- **Maksimum:** < 30 saniye (timeout)

### PR-2: Doğruluk
- **Ana bölüm tespiti:** %90+
- **Alt bölüm tespiti:** %80+
- **İndeks doğruluğu:** %95+ (±5 karakter)

### PR-3: Güvenilirlik
- **Şema uyumu:** %99+
- **Hallucination:** < %5

---

## Test Gereksinimleri

### Test-1: Unit Tests
- **Dosya:** `llm/tests/test_faithful.py`
- **Kapsam:**
  - XML yapı doğrulama
  - İçerik değişikliği kontrolü
  - İndeks doğruluğu
  - Overlap kontrolü
  - Hiyerarşi kontrolü

### Test-2: Integration Tests
- Örnek raporlarla end-to-end test
- Model değişimi testleri
- Hata durumu testleri

### Test-3: Örnek Veriler
- `data/sample_reports/` klasörüne kendi PDF dosyalarınızı koyun
  - Türkçe rapor
  - İngilizce rapor
  - Karışık format raporu

---

## Mimari Tasarım

### Modül Yapısı

```
llm/
├── tools/
│   └── gemini_segment.py      # Ana segmentasyon fonksiyonu
├── prompts/
│   └── segmentation.json.txt   # LLM prompt şablonu (JSON formatı)
├── schemas/
│   ├── section.schema.json    # Çıktı şeması
│   └── example_output.json    # Örnek çıktı
└── tests/
    └── test_faithful.py       # Test suite
```

### API Arayüzü (Planlanan)

```python
def segment_document(
    text: str,
    model: str = "gemini-1.5-flash",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Staj raporu metnini bölümlere ayırır.
    
    Args:
        text: PDF/DOCX'den çıkarılmış düz metin
        model: LLM model adı (gemini-1.5-flash, gpt-4o-mini)
        api_key: API anahtarı (opsiyonel, env'den alınır)
    
    Returns:
        Şema uyumlu JSON dict (segmentation + metadata)
    
    Raises:
        ValueError: Şema uyumsuzluğu
        RuntimeError: API hatası
    """
```

---

## Bağımlılıklar

### Python Paketleri
- `google-generativeai` (Gemini API)
- `openai` (fallback için)
- `pydantic` (şema doğrulama, gelecek hafta)
- `xml.etree.ElementTree` (XML parsing)

### Harici Servisler
- Google Gemini API (birincil)
- OpenAI API (fallback)

---

## Güvenlik ve Etik

### G-1: API Key Yönetimi
- API anahtarları environment variable'da saklanır
- Kod deposuna commit edilmez
- `.env` dosyası `.gitignore`'da

### G-2: Veri Gizliliği
- Rapor metinleri geçici olarak işlenir
- LLM API'ye gönderilen veriler loglanmaz
- Anonimleştirme (gelecek hafta)

---

## Gelecek Geliştirmeler (Hafta 2+)

- [ ] Pydantic şema doğrulama
- [ ] Regex/heuristic guardrail'ler
- [ ] Otomatik başlık doğrulama
- [ ] Batch processing desteği
- [ ] Cache mekanizması
- [ ] Metrik toplama (doğruluk, süre)

---

## Rubric Referansı

### Notlandırma Kriterleri (Ağırlıklar)

1. **Executive Summary** - 6%
2. **Overview of the Company and Sector** - 8%
3. **Professional and Ethical Responsibilities** - 8% (Level 2, Company and Sector altında)
4. **Activity Analysis / Project** - 40% (EN ÖNEMLİ)
5. **Conclusion** - 6%
6. **Impact** - 8% (Level 2, Conclusion altında)
7. **Team Work** - 6% (Level 2, Conclusion altında)
8. **Self-directed Learning** - 8% (Level 2, Conclusion altında)
9. **Format and Organisation** - 10%

### Kritik Hiyerarşi Kuralları

- **Professional and Ethical Responsibilities** → MUTLAKA Level 2 (parent_id = company_sector)
- **Impact, Team Work, Self-directed Learning** → MUTLAKA Level 2 (parent_id = conclusion)
- **Daily Activities** → MUTLAKA Level 2 (parent_id = activity_analysis), günler birleşik
- **Activity Analysis / Project** → TEK Level 1 bölüm, içindeki aktiviteler ayrı Level 1 yapma

---

## Referanslar

- JSON Şema: `llm/schemas/section.schema.json`
- Örnek Çıktı: `llm/schemas/example_output.json`
- Prompt: `llm/prompts/segmentation.json.txt`
- Model Karşılaştırması: `llm/docs/model_comparison.md`
- Bölümleme Analizi: `llm/docs/segmentation_analysis.md`
- Rubric: Internship Grading Rubric 2021

