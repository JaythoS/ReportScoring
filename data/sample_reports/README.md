# Sample Reports Klasörü

Bu klasöre kendi PDF dosyalarınızı koyabilirsiniz.

## 📁 Kullanım

1. **PDF dosyalarınızı bu klasöre kopyalayın:**
   ```
   data/sample_reports/
   ├── rapor1.pdf
   ├── rapor2.pdf
   └── rapor3.pdf
   ```

2. **Demo'yu çalıştırın:**
   ```bash
   # İlk PDF'i otomatik kullanır
   python llm/tools/demo_live.py
   
   # Veya belirli bir dosya belirtin
   python llm/tools/demo_live.py --file data/sample_reports/rapor1.pdf
   ```

## 📝 Desteklenen Formatlar

- ✅ PDF (`.pdf`) - Otomatik olarak metne çevrilir
- ✅ DOCX (`.docx`) - Otomatik olarak metne çevrilir
- ❌ TXT (`.txt`) - Desteklenmez (staj raporları PDF/DOCX formatında olmalı)

## ⚠️ Not

- Dosyalar bu klasörde kalır, silinmez
- PDF'ler otomatik olarak metne çevrilir
- Çıktılar proje kök dizinine kaydedilir

