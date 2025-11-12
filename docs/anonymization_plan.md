# 🔒 Anonimleştirme Planı - GDPR/KVKK Uyumluluğu

## 🎯 Genel Bakış

Bu dokümantasyon, staj raporlarında bulunan kişisel verilerin anonimleştirilmesi için strateji ve implementasyon planını içerir.

## 📋 Tespit Edilen Kişisel Veriler

### 1. Öğrenci Bilgileri
- **İsim:** Öğrenci adı ve soyadı (örn: "Helin Dinçel")
- **Öğrenci ID:** Öğrenci numarası (örn: "042101121")
- **Üniversite:** Üniversite adı (örn: "MEF University")
- **Program:** Program adı (örn: "Computer Engineering Program")

### 2. Şirket Bilgileri
- **Şirket Adı:** Şirket adı (örn: "Core4Basis Teknoloji ve Danışmanlık Hizmetleri")
- **Adres:** Fiziksel adres (örn: "Nida Kule Batı Plaza, Barbaros Mah. Begonya Sok. No:1 Ataşehir/İstanbul")
- **Email:** E-posta adresi (örn: "info@core4basis.com")
- **Telefon:** Telefon numarası (örn: "+90 532 382 10 26")
- **Website:** Web sitesi URL'si (örn: "https://www.core4basis.com")

### 3. Diğer Kişisel Veriler
- **Müdür İsmi:** Supervisor adı (varsa)
- **Tarihler:** Staj tarihleri (tarih aralıkları)
- **Müşteri İsimleri:** Müşteri şirket isimleri (varsa)

## 🔒 Anonimleştirme Stratejisi

### Yaklaşım 1: Regex Pattern Masking (Birincil)

**Avantajlar:**
- Hızlı ve etkili
- Basit implementasyon
- Yüksek doğruluk oranı
- Reversible (mapping dosyası ile)

**Dezavantajlar:**
- False positive'ler olabilir
- Bağlam bilgisi eksik

### Yaklaşım 2: Named Entity Recognition (NER) (İkincil)

**Avantajlar:**
- Bağlam bilgisi ile daha doğru
- False positive'ler daha az
- Entity türleri ayırt edilebilir

**Dezavantajlar:**
- Daha yavaş
- Model bağımlılığı
- Ekstra dependency

### Yaklaşım 3: Hybrid (Önerilen)

**Strateji:**
1. Regex pattern'leri ile hızlı maskeleme
2. NER ile doğrulama ve iyileştirme
3. Mapping dosyası ile reversible anonimleştirme

## 📝 Regex Pattern'leri

### 1. Öğrenci İsmi
```python
# Türkçe isim pattern'i
STUDENT_NAME_PATTERN = r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\b'
# Örnek: "Helin Dinçel" → "[STUDENT_NAME]"
```

### 2. Öğrenci ID
```python
# 9 haneli öğrenci numarası
STUDENT_ID_PATTERN = r'\b\d{9}\b'
# Örnek: "042101121" → "[STUDENT_ID]"
```

### 3. Email
```python
# Email adresi
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
# Örnek: "info@core4basis.com" → "[EMAIL]"
```

### 4. Telefon
```python
# Türk telefon numarası
PHONE_PATTERN = r'(\+90\s?)?(\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|\d{10})'
# Örnek: "+90 532 382 10 26" → "[PHONE]"
```

### 5. Adres
```python
# Türk adres pattern'i
ADDRESS_PATTERN = r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+Mah\.|Sok\.|Cad\.|No:\d+|[A-ZÇĞİÖŞÜ][a-zçğıöşü]+/[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\b'
# Örnek: "Barbaros Mah. Begonya Sok. No:1 Ataşehir/İstanbul" → "[ADDRESS]"
```

### 6. Website
```python
# URL pattern'i
URL_PATTERN = r'https?://[^\s]+'
# Örnek: "https://www.core4basis.com" → "[URL]"
```

### 7. Şirket Adı
```python
# Şirket adı (bağlam bazlı)
COMPANY_NAME_PATTERN = r'Company Name:\s*([^\n]+)'
# Örnek: "Company Name: Core4Basis Teknoloji" → "Company Name: [COMPANY_NAME]"
```

## 🔧 Implementasyon Planı

### Adım 1: Anonimleştirme Modülü Oluştur
- `scripts/anonymize.py` - Ana anonimleştirme scripti
- Regex pattern'leri tanımla
- Masking fonksiyonları oluştur

### Adım 2: Mapping Dosyası
- `data/processed/anonymization_mappings/` - Mapping dosyaları
- `report_XXX_mapping.json` - Her rapor için mapping
- Reversible anonimleştirme için

### Adım 3: Test ve Doğrulama
- Test verileri ile test et
- False positive'leri kontrol et
- Doğruluk oranını ölç

### Adım 4: Entegrasyon
- Pipeline'a entegre et
- Otomatik anonimleştirme
- Metadata'ya anonimleştirme bilgisi ekle

## 📊 Anonimleştirme Mapping Formatı

```json
{
  "report_id": "report_001",
  "anonymization_timestamp": "2024-11-08T10:30:00Z",
  "mappings": {
    "STUDENT_NAME": {
      "original": "Helin Dinçel",
      "anonymized": "[STUDENT_NAME_001]",
      "pattern": "STUDENT_NAME_PATTERN",
      "count": 15
    },
    "STUDENT_ID": {
      "original": "042101121",
      "anonymized": "[STUDENT_ID_001]",
      "pattern": "STUDENT_ID_PATTERN",
      "count": 3
    },
    "EMAIL": {
      "original": "info@core4basis.com",
      "anonymized": "[EMAIL_001]",
      "pattern": "EMAIL_PATTERN",
      "count": 1
    },
    "PHONE": {
      "original": "+90 532 382 10 26",
      "anonymized": "[PHONE_001]",
      "pattern": "PHONE_PATTERN",
      "count": 1
    },
    "ADDRESS": {
      "original": "Nida Kule Batı Plaza, Barbaros Mah. Begonya Sok. No:1 Ataşehir/İstanbul",
      "anonymized": "[ADDRESS_001]",
      "pattern": "ADDRESS_PATTERN",
      "count": 1
    },
    "URL": {
      "original": "https://www.core4basis.com",
      "anonymized": "[URL_001]",
      "pattern": "URL_PATTERN",
      "count": 1
    },
    "COMPANY_NAME": {
      "original": "Core4Basis Teknoloji ve Danışmanlık Hizmetleri",
      "anonymized": "[COMPANY_NAME_001]",
      "pattern": "COMPANY_NAME_PATTERN",
      "count": 5
    }
  },
  "statistics": {
    "total_replacements": 27,
    "patterns_used": 7,
    "anonymization_rate": 0.95
  }
}
```

## 🔒 Güvenlik ve Uyumluluk

### GDPR/KVKK Gereksinimleri
- ✅ Kişisel veriler anonimleştirilmeli
- ✅ Mapping dosyaları güvenli saklanmalı
- ✅ Anonimleştirme işlemi dokümante edilmeli
- ✅ Geri dönüşüm (reversibility) için mapping saklanmalı

### Güvenlik Kuralları
- Mapping dosyaları `.gitignore`'da olmalı
- Mapping dosyaları şifrelenmiş saklanmalı
- Erişim kontrolü olmalı

## 📋 Kullanım Senaryoları

### Senaryo 1: Tek Rapor Anonimleştirme
```bash
python scripts/anonymize.py --input data/processed/texts/report_001.txt --output data/processed/anonymized/report_001_anonymized.txt
```

### Senaryo 2: Batch Anonimleştirme
```bash
python scripts/anonymize.py --batch --input-dir data/processed/texts --output-dir data/processed/anonymized
```

### Senaryo 3: Mapping ile Reversible Anonimleştirme
```bash
python scripts/anonymize.py --input data/processed/texts/report_001.txt --output data/processed/anonymized/report_001_anonymized.txt --save-mapping data/processed/anonymization_mappings/report_001_mapping.json
```

## ✅ Test Kriterleri

### Doğruluk Kriterleri
- ✅ Tüm kişisel veriler tespit edilmeli (%95+)
- ✅ False positive oranı < %5
- ✅ Anonimleştirme sonrası metin okunabilir olmalı
- ✅ Mapping dosyası doğru oluşturulmalı

### Performans Kriterleri
- ✅ Tek rapor için < 1 saniye
- ✅ Batch işleme için < 10 saniye (100 rapor)

## 🎯 Sonraki Adımlar

1. ✅ Anonimleştirme planı oluşturuldu
2. ✅ Anonimleştirme modülü implementasyonu
3. ✅ Test ve doğrulama
4. ⏭️ Pipeline entegrasyonu
5. ✅ Dokümantasyon güncelleme

