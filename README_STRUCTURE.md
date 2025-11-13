# Yeni Proje Yapısı

## ✅ Tamamlanan Yeniden Yapılandırma

Proje modüler ve organize bir yapıya kavuşturuldu.

## 📁 Yeni Yapı

```
ReportScoring/
├── core/                    # ✅ Ana işlevsel modüller
│   ├── anonymization/       # ✅ Anonimleştirme
│   ├── scoring/             # ✅ Notlandırma
│   ├── segmentation/        # ✅ Segmentasyon
│   └── extraction/          # ✅ Metin çıkarma
│
├── llm/                     # ✅ LLM işlemleri (prompts, tools)
├── scripts/                 # ✅ CLI Scriptleri (organize edildi)
│   ├── anonymization/
│   ├── scoring/
│   ├── segmentation/
│   └── pipeline/
├── data/                    # ✅ Veri klasörü
├── outputs/                 # ✅ Çıktılar (organize edildi)
│   ├── segmentations/
│   ├── cover_scores/
│   └── executive_scores/
└── docs/                    # ✅ Dokümantasyon
```

## 🔄 Migration Durumu

### ✅ Tamamlanan
- Core modüller oluşturuldu
- Scripts organize edildi
- Outputs organize edildi
- Import path'leri güncellendi

### ⚠️ Backward Compatibility
Eski import'lar hala çalışıyor:
- `llm.tools.*` → `core.*` (otomatik fallback)
- `src.analyze.*` → `core.scoring.*` (otomatik fallback)

### 📝 Yeni Kullanım

```python
# Yeni yapı (önerilen)
from core.extraction import extract_text_from_pdf
from core.segmentation import segment_text_chunked
from core.scoring import score_cover_segment
from core.anonymization import anonymize_file

# Eski yapı (hala çalışıyor)
from llm.tools.pdf_extractor import extract_text
from src.analyze.segment_scoring import score_segment
```

## 🎯 Avantajlar

1. **Modüler Yapı**: Her modül bağımsız
2. **Temiz Organizasyon**: İlgili dosyalar birlikte
3. **Kolay Bakım**: Değişiklikler izole
4. **Test Edilebilir**: Her modül ayrı test edilebilir
5. **Genişletilebilir**: Yeni modüller kolayca eklenebilir

## 📚 Detaylı Dokümantasyon

- `PROJECT_STRUCTURE.md` - Detaylı yapı açıklaması
- `core/README.md` - Core modüller açıklaması
- `scripts/README.md` - Scripts kullanımı

