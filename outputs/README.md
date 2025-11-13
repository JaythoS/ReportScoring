# Outputs Klasör Yapısı

Bu klasör tüm işleme sonuçlarını içerir. Yapı şu şekilde organize edilmiştir:

## Klasör Yapısı

```
outputs/
├── segmentations/          # Segmentasyon sonuçları
│   ├── *.json              # Ham segmentasyon dosyaları
│   └── *.fixed.json        # Düzeltilmiş segmentasyon dosyaları
├── cover_scores/           # Cover (Kapak) notlandırma sonuçları
│   └── *_cover_score_*.json
└── executive_scores/        # Executive Summary notlandırma sonuçları
    └── *_executive_score_*.json
```

## Klasör Açıklamaları

### `segmentations/`
PDF dosyalarının segmentasyon sonuçları. Her PDF için iki dosya oluşturulur:
- `{dosya_adi}_Rubric_v3_{timestamp}.json` - Ham segmentasyon
- `{dosya_adi}_Rubric_v3_{timestamp}.fixed.json` - Düzeltilmiş segmentasyon

### `cover_scores/`
Cover (kapak sayfası) bölümünün notlandırma sonuçları. Her dosya şu bilgileri içerir:
- Toplam puan (0-10)
- 4 kriter puanı (title_accuracy, format, completeness, date_name_presence)
- Detaylı feedback

### `executive_scores/`
Executive Summary bölümünün notlandırma sonuçları. Her dosya şu bilgileri içerir:
- Toplam puan (0-10)
- 5 kriter puanı (main_engineering_activities, major_internship_activities, expectations_and_outcomes, learning_and_benefits, reader_engagement)
- Detaylı feedback

## Oluşturma

### Segmentasyon
Segmentasyon otomatik olarak scoring scriptleri tarafından oluşturulur.

### Cover Scoring
```bash
python scripts/scoring/score_cover.py --pdf dosya.pdf
```

### Executive Summary Scoring
```bash
python scripts/scoring/score_executive.py --pdf dosya.pdf
```

## Dosya İsimlendirme

Tüm dosyalar şu formatta isimlendirilir:
- `{güvenli_dosya_adi}_{tip}_score_{timestamp}.json`

Örnek:
- `ömer_bilbil_cover_score_20251112_184746.json`
- `ömer_bilbil_executive_score_20251112_184746.json`

