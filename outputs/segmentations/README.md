# Segmentation Çıktıları (Rubric-Based)

Bu klasör, her PDF/DOCX staj raporu için yapılan bölümleme (segmentation) işlemlerinin JSON çıktılarını içerir. Tüm çıktılar **notlandırma rubric'ine göre** yapılandırılmıştır.

## Dosya Adlandırma

Her dosya şu formatta adlandırılır:
```
PDF_ADI_TIMESTAMP.json
```

Örnek:
- `Doguş_Teknoloji_Intern_Report_LAST_20241105_140530.json`
- `Core4Basis_Intern_Report_SON_20241105_141205.json`

## İçerik

Her JSON dosyası şu yapıya sahiptir:
```json
{
  "segmentation": {
    "sections": [
      {
        "section_id": "unique_id",
        "section_name": "Bölüm başlığı",
        "content": "Bölüm içeriği",
        "start_idx": 0,
        "end_idx": 100,
        "level": 1,
        "parent_id": null
      }
    ]
  },
  "source_metadata": {
    "total_length": 1000,
    "extraction_timestamp": "2024-11-05T14:05:30"
  }
}
```

## Rubric Yapısı

Çıktılar rubric kriterlerine göre yapılandırılmıştır:
- **Level 1:** Cover, Executive Summary, Company and Sector, Activity Analysis / Project, Conclusion, References
- **Level 2:** Professional and Ethical Responsibilities (Company and Sector altında), Impact, Team Work, Self-directed Learning (Conclusion altında), Daily Activities (Activity Analysis altında)
- **Hiyerarşi:** Kritik bölümler parent_id ile doğru ilişkilendirilmiştir

## Dosya Türleri

- `.json` - Ham LLM çıktısı
- `.fixed.json` - Post-processing sonrası düzeltilmiş çıktı (overlap/gap düzeltmeleri)

## Notlar

- Her segmentation işlemi için yeni bir dosya oluşturulur
- Eski dosyalar otomatik olarak silinmez
- Parse hatası olsa bile ham çıktı kaydedilir
- Rubric'e göre bölüm sayısı: ~15-20 bölüm (Level 1: 5-7, Level 2: 8-12)

