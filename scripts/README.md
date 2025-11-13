# Scripts

CLI scriptleri bu klasörde bulunur. Her modül için ayrı klasörler:

## Klasör Yapısı

```
scripts/
├── anonymization/         # Anonimleştirme scriptleri
│   └── anonymize.py
├── scoring/               # Scoring scriptleri
│   ├── score_cover.py
│   ├── score_executive.py
│   ├── test_with_real_scores.py
│   └── common.py
├── segmentation/          # Segmentasyon scriptleri
└── pipeline/              # Pipeline scriptleri
│   └── run_pipeline.py
```

## Kullanım

### Scoring
```bash
# Cover notlandırma
python scripts/scoring/score_cover.py --pdf dosya.pdf

# Executive Summary notlandırma
python scripts/scoring/score_executive.py --pdf dosya.pdf

# Gerçek notlarla test
python scripts/scoring/test_with_real_scores.py --limit 10
```

### Anonymization
```bash
# Tek dosya
python scripts/anonymization/anonymize.py --input rapor.txt --output rapor_anon.txt

# Batch işleme
python scripts/anonymization/anonymize.py --batch --input-dir data/processed/texts --output-dir data/processed/anonymized
```

### Pipeline
```bash
# Tam pipeline
python scripts/pipeline/run_pipeline.py --pdf dosya.pdf
```

