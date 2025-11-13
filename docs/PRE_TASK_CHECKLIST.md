# ✅ Görevler Öncesi Kontrol Listesi

## 🔍 Mevcut Durum Analizi

### ✅ Yapılmış Olanlar
- ✅ PDF/DOCX metin çıkarma scripti (`llm/tools/pdf_extractor.py`)
- ✅ Segmentation pipeline (`llm/tools/run_segmentation.py`)
- ✅ Validation mekanizması
- ✅ Basic data structure (`data/sample_reports/`)
- ✅ Segmentation output şeması (`llm/schemas/section.schema.json`)

### ❌ Eksik Olanlar (Yapılması Gerekenler)

## 🚨 ÖNCE YAPILMASI GEREKENLER

### 1. **Veri Yapısı Planı ve Oluşturma** ⚠️ KRİTİK
**Durum:** Sadece `data/sample_reports/` var, organize yapı yok  
**Neden Önemli:** 150 rapor için düzenli klasör yapısı şart  
**Yapılacaklar:**
- [ ] `data/raw/` - Ham PDF/DOCX dosyaları (150 rapor)
- [ ] `data/processed/` - İşlenmiş metinler ve segmentasyonlar
- [ ] `data/train/` - Eğitim seti (120 rapor)
- [ ] `data/test/` - Test seti (30 rapor)
- [ ] Her klasör için README.md
- [ ] Dosya adlandırma standardı

**Sıra:** İLK YAPILMASI GEREKEN (diğer her şey buna bağlı)

---

### 2. **Metadata Şeması Tanımı** ⚠️ KRİTİK
**Durum:** Sadece `source_metadata` var segmentation çıktılarında  
**Neden Önemli:** Her rapor için puan, kriterler, işlem tarihi saklanmalı  
**Yapılacaklar:**
- [ ] `metadata.json` şema dosyası oluştur
- [ ] Alanlar: dosya adı, puan, kriterler, işlem tarihi, hash
- [ ] Şema validation scripti
- [ ] Örnek metadata.json dosyası

**Sıra:** 2. Sırada (veri yapısından sonra)

---

### 3. **Anonimleştirme Planı** ⚠️ YASAL GEREKLİLİK
**Durum:** SystemSpec'te "gelecek hafta" yazıyor, hiç yok  
**Neden Önemli:** GDPR/KVKK uyumluluğu için zorunlu  
**Yapılacaklar:**
- [ ] Anonimleştirme stratejisi dokümantasyonu
- [ ] Regex pattern'leri (isim, email, telefon, adres)
- [ ] Entity masking planı
- [ ] Test scripti

**Sıra:** 3. Sırada (metadata'dan sonra, pipeline test'ten önce)

---

### 4. **Pipeline Test Scripti Hazırlığı** ⚠️ ÖNEMLİ
**Durum:** Sadece tek dosya için script var  
**Neden Önemli:** 150 raporu toplu işlemek için gerekli  
**Yapılacaklar:**
- [ ] Batch processing scripti
- [ ] Error handling ve retry mekanizması
- [ ] Progress tracking
- [ ] Log sistemi

**Sıra:** 4. Sırada (veri yapısı ve metadata'dan sonra)

---

## 📋 ÖNERİLEN ÇALIŞMA SIRASI

```
1. Veri Yapısı Oluştur
   ↓
2. Metadata Şeması Tanımla
   ↓
3. Anonimleştirme Planı Oluştur
   ↓
4. Pipeline Test Scripti Hazırla
   ↓
5. Mock 3 Raporla Test Et
   ↓
6. SystemSpec Data Flow & Ethics Yaz
```

---

## ⚠️ DİKKAT EDİLMESİ GEREKENLER

### Veri Güvenliği
- ✅ `.gitignore` dosyasını kontrol et (PDF/DOCX dosyaları commit edilmemeli)
- ✅ API key'ler environment variable'da
- ⚠️ Kişisel veriler (isim, email) anonimleştirilmeli

### Veri Yapısı
- ✅ Klasör yapısı tutarlı olmalı
- ✅ Dosya adlandırma standardı oluştur
- ✅ README.md dosyaları her klasörde

### Metadata
- ✅ Her rapor için benzersiz ID
- ✅ İşlem tarihi ve hash bilgisi
- ✅ Puan ve kriterler JSON formatında

---

## 🎯 HAZIR OLMA KRİTERLERİ

Görevlere başlamadan önce şunlar hazır olmalı:

- [ ] `data/raw/`, `data/processed/`, `data/train/`, `data/test/` klasörleri var
- [ ] `metadata.json` şeması tanımlı ve dokümante
- [ ] Anonimleştirme planı hazır (dokümantasyon)
- [ ] Pipeline test scripti hazır (en azından taslak)
- [ ] `.gitignore` dosyası güncel (PDF/DOCX, metadata.json eklenmeli)

---

## 📝 SONRAKİ ADIMLAR

Görevler listesine başlamadan önce:

1. ✅ Bu checklist'i oku ve anla
2. ✅ Veri yapısını oluştur
3. ✅ Metadata şemasını tanımla
4. ✅ Anonimleştirme planını hazırla
5. ✅ Görevlere başla

---

## 🔗 İLGİLİ DOSYALAR

- Veri yapısı: `data/` klasörü
- Metadata şeması: `schemas/metadata.schema.json` (oluşturulacak)
- Anonimleştirme: `docs/anonymization_plan.md` (oluşturulacak)
- SystemSpec: `docs/system_spec_llm_segmenter.md`

