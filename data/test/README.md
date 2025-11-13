# 📁 Test Data - Test Seti

## 🎯 Amaç

Bu klasör, model değerlendirmesi için kullanılacak raporları içerir.

## 📊 İstatistikler

- **Toplam Rapor:** 30
- **Oran:** %20 (150'nin %20'si)
- **Kaynak:** `raw/` klasöründen kopyalanır

## 📂 Klasör Yapısı

```
test/
├── report_121.pdf
├── report_122.pdf
├── ...
└── report_150.pdf
```

## 🔄 Oluşturma

Test seti, `raw/` klasöründeki son 30 raporun kopyalanması ile oluşturulur.

### Train/Test Ayrımı Stratejisi

**Seçenek 1: Sıralı Ayrım**
- İlk 120 rapor → Train
- Son 30 rapor → Test

**Seçenek 2: Rastgele Ayrım (Önerilen)**
- 150 rapor rastgele karıştırılır
- İlk 120 rapor → Train
- Son 30 rapor → Test
- Ayrım bilgisi `data/split_info.json` dosyasına kaydedilir

## 📋 Kullanım

Test seti şu amaçlarla kullanılır:
1. Model değerlendirmesi
2. Final performans ölçümü
3. Generalization testi
4. Model karşılaştırması

## ⚠️ Önemli Notlar

1. **Git Ignore:** Bu klasör `.gitignore`'da olmalı
2. **Değiştirilmez:** Test seti sabit kalmalı
3. **Ayrım:** Test seti train setinden ayrı tutulmalı
4. **Yedekleme:** Test seti yedeklenmeli

## 🔗 İlgili Klasörler

- Ham veriler: `../raw/`
- Train seti: `../train/`
- İşlenmiş veriler: `../processed/`

