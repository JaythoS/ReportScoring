# Bölümleme İşlevi Analizi - Rubric-Based

## Genel Bakış

Staj raporlarını **notlandırma rubric'ine göre** bölümlere ayırma işlevi. Amaç: **Faithful extraction** - orijinal metni değiştirmeden, karakter-pozisyonlu alıntılar ile bölüm çıkarımı. Her bölüm rubric'teki kriterlere göre puanlanacaktır.

**Rubric Referansı:** Internship Grading Rubric 2021

---

## Rubric'e Göre Bölüm Yapısı

### Ana Bölümler (Level 1) - Rubric Kriterleri

1. **Cover (Kapak)** - Format and Organisation (10%)
   - Title, university, program, tarih birleşik
   - Tek Level 1 bölüm

2. **Executive Summary** - 6% ağırlık
   - Engineering activities, internship activities, learned benefits, expectations, outcomes
   - Tek Level 1 bölüm (başlık + içerik birleşik)

3. **Overview of the Company and Sector** - 8% ağırlık
   - Company info: name, address, history, employees, ownership
   - Organization chart, departments
   - Production/service components
   - Alt bölümler (Level 2):
     - a) Overview of the Company and Sector
     - b) Organization of the Company
     - c) Production/Service System
     - d) Professional and Ethical Responsibilities of Engineers (8% ağırlık, Level 2)

4. **Activity Analysis / Project** - 40% ağırlık (EN ÖNEMLİ BÖLÜM)
   - IE activities related to major studies
   - Clear explanation of activities/projects
   - Scientific problem detection
   - Definition of IE problems
   - Proposed improvements
   - Measurable performance improvement
   - Alt bölümler (Level 2):
     - Main List of Activities
     - Activity Analysis
     - Project
     - Daily Activities (günler birleşik, tek Level 2 bölüm)

5. **Conclusion** - 6% ağırlık
   - Evaluation of internship activities
   - Current state and major challenges
   - Future changes with emerging technologies
   - Alt bölümler (Level 2):
     - Impact (8% ağırlık)
     - Team Work (6% ağırlık)
     - Self-directed Learning (8% ağırlık)

6. **References** - Format and Organisation için (opsiyonel)
   - Referans listesi

### Kritik Hiyerarşi Kuralları (Rubric'e Göre)

**MUTLAKA Level 2 Olması Gerekenler:**
- **Professional and Ethical Responsibilities** → parent_id = company_sector section_id
- **Impact** → parent_id = conclusion section_id
- **Team Work** → parent_id = conclusion section_id
- **Self-directed Learning** → parent_id = conclusion section_id
- **Daily Activities** → parent_id = activity_analysis section_id (günler birleşik)

**Birleşik Olması Gerekenler:**
- Cover: Title, university, program → Tek Level 1 bölüm
- Executive Summary: Başlık + içerik → Tek Level 1 bölüm
- Activity Analysis / Project: Tüm aktiviteler → Tek Level 1 bölüm, alt bölümler Level 2

---

## Bölüm Tanıma Kuralları

### Başlık Formatları

1. **Sayısal başlıklar:**
   - "1. Giriş"
   - "2.1 Kullanılan Teknolojiler"
   - "3. SONUÇLAR"

2. **Metin başlıkları:**
   - "Giriş"
   - "Introduction"
   - "YÖNTEM"
   - "Methodology"

3. **Boşluk ve formatlamalar:**
   - Başlıklardan önce/sonra boş satırlar olabilir
   - Bold/italik formatları görmezden gelinmeli (metin çıkarımında)

### Hiyerarşi Tespiti

- **Level 1:** Başlık büyük harfle başlıyorsa, sayfa başında ise, font boyutu büyükse
- **Level 2:** "1.1", "2.1" gibi alt numaralandırmalar
- **Level 3:** "1.1.1", "2.1.1" gibi

---

## Faithful Extraction Gereksinimleri

### Kritik Kurallar

1. **Değiştirme YASAK:**
   - Kelime ekleme/çıkarma yok
   - Yazım düzeltmesi yok
   - Özet çıkarma yok
   - Sadece orijinal metni kopyala-yapıştır

2. **Karakter Pozisyonu Zorunluluğu:**
   - Her bölüm için `start_idx` ve `end_idx` doğru olmalı
   - İndeksler kaynak metindeki gerçek pozisyonları yansıtmalı

3. **Kapsama:**
   - Tüm metin kapsanmalı (gaps olmamalı)
   - Bölümler örtüşmemeli (minimal overlap sadece whitespace)

4. **Hallucination Önleme:**
   - Olmayan bölümler eklenmemeli
   - Metinde bahsedilmeyen başlıklar oluşturulmamalı

---

## İşlem Akışı

```
PDF/DOCX → Metin Çıkarımı → LLM Bölümleme → XML/JSON Çıktı
                                    ↓
                           Doğrulama (şema, indeks)
                                    ↓
                           Test (faithful extraction)
```

### 1. Metin Çıkarımı
- PDF: PyPDF2, pdfplumber, veya Tesseract OCR
- DOCX: python-docx
- Çıktı: Düz metin + (opsiyonel) sayfa numaraları

### 2. LLM Bölümleme
- Prompt: XML-structured, şema zorunlu
- Model: Gemini 1.5 Flash (varsayılan)
- Çıktı: XML veya JSON (şemaya uygun)

### 3. Doğrulama
- XML/JSON şema validation
- İndeks doğruluk kontrolü
- Overlap kontrolü

### 4. Test
- Faithful extraction testleri
- Karakter karşılaştırma
- Hallucination tespiti

---

## Özel Durumlar

### Eksik Bölümler
- Eğer bir rapor "Giriş" bölümü olmadan başlıyorsa → İlk paragrafı "Giriş" olarak işaretle
- Eğer "Yöntem" yoksa → "Sonuçlar" bölümünü tek bölüm olarak al

### Karışık Diller
- Türkçe başlık + İngilizce içerik → Bölüm adını Türkçe olarak al
- Her iki dilde de aynı anlama gelen başlıklar → Orijinal metindekini kullan

### Formatlamalar
- Tablo/şekil başlıkları → Alt bölüm olarak değil, içerik parçası olarak işle
- Dipnotlar → Ana içeriğe dahil et

---

## Çıktı Formatı

### XML Formatı
```xml
<segmentation>
  <sections>
    <section>
      <section_id>intro_1</section_id>
      <section_name>Giriş</section_name>
      <content>...</content>
      <start_idx>0</start_idx>
      <end_idx>145</end_idx>
      <level>1</level>
      <parent_id>null</parent_id>
    </section>
  </sections>
</segmentation>
```

### JSON Formatı
Bkz: `schemas/section.schema.json`

---

## Başarı Kriterleri (Rubric'e Göre)

1. ✅ Rubric kriterlerine karşılık gelen tüm bölümler tespit edilmeli
   - Executive Summary (6%)
   - Company and Sector (8%)
   - Professional and Ethical Responsibilities (8%, Level 2)
   - Activity Analysis / Project (40% - EN ÖNEMLİ)
   - Conclusion (6%)
   - Impact, Team Work, Self-directed Learning (Level 2, Conclusion altında)
2. ✅ Hiyerarşi doğru olmalı (kritik bölümler Level 2, parent_id doğru)
3. ✅ İçerik %100 orijinal metinden, değiştirilmeden
4. ✅ Karakter indeksleri doğru (±5 karakter tolerans)
5. ✅ Hallucination oranı < %5
6. ✅ Birleşik bölümler doğru (Cover, Executive Summary, Daily Activities birleşik)

---
