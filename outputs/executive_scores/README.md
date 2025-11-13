# Executive Summary Scores

Bu klasör Executive Summary bölümünün notlandırma sonuçlarını içerir.

## Dosya Formatı

Her JSON dosyası şu yapıda:

```json
{
  "pdf_file": "dosya_adi.pdf",
  "segmentation_file": "segmentation_dosyasi.fixed.json",
  "segment": {
    "section_id": "executive_summary_1",
    "section_name": "Executive Summary",
    "content": "...",
    "level": 1,
    "parent_id": null
  },
  "score": {
    "total_score": 7.4,
    "criteria": {
      "main_engineering_activities": 7.0,
      "major_internship_activities": 8.0,
      "expectations_and_outcomes": 6.0,
      "learning_and_benefits": 8.0,
      "reader_engagement": 8.0
    },
    "feedback": "..."
  },
  "timestamp": "2025-11-12T18:47:46.055133"
}
```

## Kriterler

- **main_engineering_activities**: Ana Mühendislik Faaliyetleri (0-10)
- **major_internship_activities**: Ana Staj Faaliyetleri (0-10)
- **expectations_and_outcomes**: Beklentiler ve Sonuçlar (0-10)
- **learning_and_benefits**: Öğrenilenler ve Faydalar (0-10)
- **reader_engagement**: Okuyucu İlgisi (0-10)

## Oluşturma

Executive Summary notlandırma scripti ile oluşturulur:

```bash
python scripts/scoring/score_executive.py --pdf dosya.pdf
```

