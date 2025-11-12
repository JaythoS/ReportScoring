# 📁 Train Data - Eğitim Seti

## 🎯 Amaç

Bu klasör, model eğitimi için kullanılacak raporları içerir.

## 📊 İstatistikler

- **Toplam Rapor:** 120
- **Oran:** %80 (150'nin %80'i)
- **Kaynak:** `raw/` klasöründen kopyalanır

## 📂 Klasör Yapısı

```
train/
├── report_001.pdf
├── report_002.pdf
├── ...
└── report_120.pdf
```

## 🔄 Oluşturma

Train seti, `raw/` klasöründeki ilk 120 raporun kopyalanması ile oluşturulur.

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

Train seti şu amaçlarla kullanılır:
1. Model eğitimi
2. Hyperparameter tuning
3. Cross-validation
4. Model geliştirme

## ⚠️ Önemli Notlar

1. **Git Ignore:** Bu klasör `.gitignore`'da olmalı
2. **Değiştirilmez:** Train seti sabit kalmalı
3. **Versiyonlama:** Train seti versiyonlanmalı
4. **Yedekleme:** Train seti yedeklenmeli

## 🔗 İlgili Klasörler

- Ham veriler: `../raw/`
- Test seti: `../test/`
- İşlenmiş veriler: `../processed/`

