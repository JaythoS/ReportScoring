# Hafta 1 Sonu - Çıktı Özeti (Basit Görünüm)

## 🎯 Ana Çıktı: Bölümlenmiş Rapor

Bir staj raporu metnini girdi olarak verdiğinizde, sistem şu çıktıyı üretir:

---

## 📥 GİRDİ
```
GİRİŞ
Bu staj raporu, 2024 yaz döneminde...

YÖNTEM
Staj süresince kullanılan geliştirme metodolojisi...

SONUÇLAR
Staj süresince üç ana modül geliştirdim...
```

---

## 📤 ÇIKTI (XML Formatı)

```xml
<segmentation>
  <sections>
    <!-- BÖLÜM 1: GİRİŞ -->
    <section>
      <section_id>intro_1</section_id>
      <section_name>GİRİŞ</section_name>
      <content>Bu staj raporu, 2024 yaz döneminde [Şirket Adı] bünyesinde...</content>
      <start_idx>0</start_idx>
      <end_idx>245</end_idx>
      <level>1</level>
    </section>
    
    <!-- BÖLÜM 2: YÖNTEM -->
    <section>
      <section_id>method_1</section_id>
      <section_name>YÖNTEM</section_name>
      <content>Staj süresince kullanılan geliştirme metodolojisi...</content>
      <start_idx>246</start_idx>
      <end_idx>345</end_idx>
      <level>1</level>
    </section>
    
    <!-- ALT BÖLÜM: Kullanılan Teknolojiler -->
    <section>
      <section_id>method_1_1</section_id>
      <section_name>Kullanılan Teknolojiler</section_name>
      <content>Proje geliştirmesinde aşağıdaki teknolojiler...</content>
      <start_idx>346</start_idx>
      <end_idx>480</end_idx>
      <level>2</level>
      <parent_id>method_1</parent_id>
    </section>
    
    <!-- ... diğer bölümler ... -->
  </sections>
</segmentation>
```

---

## 📊 Tablo Görünümü

| Bölüm ID | Bölüm Adı | Seviye | Pozisyon | İçerik Uzunluğu |
|----------|-----------|--------|----------|-----------------|
| `intro_1` | GİRİŞ | 1 | 0-245 | 245 karakter |
| `method_1` | YÖNTEM | 1 | 246-345 | 99 karakter |
| `method_1_1` | Kullanılan Teknolojiler | 2 | 346-480 | 134 karakter |
| `method_1_2` | Geliştirme Süreci | 2 | 481-620 | 139 karakter |
| `results_1` | SONUÇLAR | 1 | 621-700 | 79 karakter |
| `results_1_1` | Kullanıcı Yönetimi Modülü | 2 | 701-840 | 139 karakter |
| `results_1_2` | Raporlama Sistemi | 2 | 841-950 | 109 karakter |
| `results_1_3` | API Entegrasyonu | 2 | 951-1080 | 129 karakter |
| `conclusion_1` | SONUÇ VE DEĞERLENDİRME | 1 | 1081-1300 | 219 karakter |

---

## 🔑 Önemli Noktalar

1. **Faithful Extraction:** İçerik orijinal metinden kelime kelime, değiştirilmeden
2. **Karakter Pozisyonları:** Her bölümün kaynak metindeki tam pozisyonu (start_idx, end_idx)
3. **Hiyerarşi:** Ana bölümler (Level 1) ve alt bölümler (Level 2+) parent_id ile bağlı
4. **Structured:** XML/JSON formatında, şema uyumlu

---

## 💻 Nasıl Kullanılır?

```python
from llm.tools.gemini_segment import segment_text

# 1. Metni bölümle
xml = segment_text(rapor_metni)

# 2. XML'i parse et
# 3. Her bölümü işle (puanlama, analiz, vb.)
```

---

**Bu çıktı hafta 2'de puanlayıcı modüle girdi olarak verilecek!**

