# Cover Scores

Bu klasör cover (kapak sayfası) bölümünün notlandırma sonuçlarını içerir.

## Dosya Formatı

Her JSON dosyası şu yapıda:

```json
{
  "pdf_file": "dosya_adi.pdf",
  "segmentation_file": "segmentation_dosyasi.fixed.json",
  "segment": {
    "section_id": "cover_1",
    "section_name": "Cover",
    "content": "...",
    "level": 1,
    "parent_id": null
  },
  "score": {
    "total_score": 8.5,
    "criteria": {
      "title_accuracy": 9.0,
      "format": 8.0,
      "completeness": 9.0,
      "date_name_presence": 8.0
    },
    "feedback": "..."
  },
  "timestamp": "2025-11-12T18:47:46.055133"
}
```

## Kriterler

- **title_accuracy**: Başlık Doğruluğu (0-10)
- **format**: Biçim (0-10)
- **completeness**: Bilgi Tamlığı (0-10)
- **date_name_presence**: Tarih/İsim Varlığı (0-10)

## Oluşturma

Cover notlandırma scripti ile oluşturulur:

```bash
python scripts/scoring/score_cover.py --pdf dosya.pdf
```

