# Core Modules

Ana işlevsel modüller burada bulunur.

## Modül Yapısı

### `anonymization/`
Anonimleştirme modülü - GDPR/KVKK uyumluluğu için kişisel verileri anonimleştirir.

**Fonksiyonlar:**
- Email, telefon, öğrenci ID, şirket adı, adres vb. anonimleştirme
- Reversible anonimleştirme (mapping dosyası ile)
- Batch işleme desteği

### `scoring/`
Notlandırma modülü - Rubrik kriterlerine göre LLM ile puanlama.

**Fonksiyonlar:**
- Cover scoring
- Executive Summary scoring
- Diğer bölümler için scoring (gelecekte eklenecek)

### `segmentation/`
Segmentasyon modülü - Raporları rubrik bölümlerine ayırır.

**Fonksiyonlar:**
- PDF/DOCX'ten metin çıkarma
- LLM ile segmentasyon
- Segmentasyon düzeltme (fix_segmentation)

### `extraction/`
Metin çıkarma modülü - PDF ve DOCX dosyalarından metin çıkarır.

**Fonksiyonlar:**
- PDF text extraction (pdfplumber/PyPDF2)
- DOCX text extraction (python-docx)

## Kullanım

Her modül bağımsız olarak kullanılabilir veya pipeline içinde birleştirilebilir.

```python
from core.extraction import extract_text_from_pdf
from core.segmentation import segment_document
from core.scoring import score_cover, score_executive_summary
from core.anonymization import anonymize_text
```

