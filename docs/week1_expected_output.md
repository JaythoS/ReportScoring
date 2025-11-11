# Hafta 1 Sonu - Beklenen Çıktı

## Genel Bakış

Hafta 1'in sonunda, bir staj raporu metnini bölümlere ayıran çalışan bir sistem hazır olacak. Sistem şu çıktıyı üretecek:

---

## 📥 Girdi (Input)

**Örnek:** Bir staj raporu metni (PDF/DOCX'ten çıkarılmış düz metin)

**Rubric'e Göre Beklenen Bölümler:**
- Executive Summary
- Company and Sector
- Activity Analysis / Project (Summer Practice Description)
- Conclusions
- Impact, Team Work, Self-directed Learning (Conclusions altında)
- Daily Activities (Activity Analysis altında)

---

## 📤 Çıktı (Output)

### Format 1: XML (Gerçek Çıktı)

```xml
<segmentation>
  <sections>
    <section>
      <section_id>intro_1</section_id>
      <section_name>GİRİŞ</section_name>
      <content>Bu staj raporu, 2024 yaz döneminde [Şirket Adı] bünyesinde gerçekleştirdiğim yazılım geliştirme stajı deneyimlerimi içermektedir. Staj süresince modern web teknolojileri ile çalışma fırsatı buldum ve endüstriyel yazılım geliştirme süreçlerini yakından gözlemleme şansı elde ettim.

Bu raporun amacı, staj süresince yaptığım çalışmaları, öğrendiklerimi ve kazandığım deneyimleri sistematik bir şekilde sunmaktır. Rapor, giriş bölümü ile başlayıp yöntem, sonuçlar ve değerlendirme bölümleriyle devam etmektedir.</content>
      <start_idx>0</start_idx>
      <end_idx>245</end_idx>
      <level>1</level>
      <parent_id>null</parent_id>
    </section>
    <section>
      <section_id>method_1</section_id>
      <section_name>YÖNTEM</section_name>
      <content>Staj süresince kullanılan geliştirme metodolojisi Agile/Scrum yaklaşımına dayanmaktadır. İki haftalık sprint dönemleri içerisinde görevler tanımlandı, geliştirildi ve test edildi.</content>
      <start_idx>246</start_idx>
      <end_idx>345</end_idx>
      <level>1</level>
      <parent_id>null</parent_id>
    </section>
    <section>
      <section_id>method_1_1</section_id>
      <section_name>Kullanılan Teknolojiler</section_name>
      <content>Proje geliştirmesinde aşağıdaki teknolojiler kullanılmıştır:
- Backend: Python 3.11, FastAPI framework
- Frontend: React 18, TypeScript, TailwindCSS
- Veritabanı: PostgreSQL 15
- Deployment: Docker, AWS EC2</content>
      <start_idx>346</start_idx>
      <end_idx>480</end_idx>
      <level>2</level>
      <parent_id>method_1</parent_id>
    </section>
    <section>
      <section_id>method_1_2</section_id>
      <section_name>Geliştirme Süreci</section_name>
      <content>Her sprint başında görevler Jira platformunda tanımlandı. Günlük stand-up toplantıları ile ilerleme takip edildi. Kod inceleme (code review) süreçleri gerçekleştirildi ve test coverage minimum %80 olarak hedeflendi.</content>
      <start_idx>481</start_idx>
      <end_idx>620</end_idx>
      <level>2</level>
      <parent_id>method_1</parent_id>
    </section>
    <section>
      <section_id>results_1</section_id>
      <section_name>SONUÇLAR</section_name>
      <content>Staj süresince üç ana modül geliştirdim ve production ortamına başarıyla deploy ettim.</content>
      <start_idx>621</start_idx>
      <end_idx>700</end_idx>
      <level>1</level>
      <parent_id>null</parent_id>
    </section>
    <section>
      <section_id>results_1_1</section_id>
      <section_name>Kullanıcı Yönetimi Modülü</section_name>
      <content>Kullanıcı kayıt, giriş, profil yönetimi ve yetkilendirme işlevlerini içeren RESTful API geliştirdim. JWT token tabanlı authentication sistemi kuruldu.</content>
      <start_idx>701</start_idx>
      <end_idx>840</end_idx>
      <level>2</level>
      <parent_id>results_1</parent_id>
    </section>
    <section>
      <section_id>results_1_2</section_id>
      <section_name>Raporlama Sistemi</section_name>
      <content>Verilerden otomatik PDF raporları üreten bir sistem geliştirdim. Raporlar haftalık, aylık ve yıllık periyotlarda oluşturulabilmektedir.</content>
      <start_idx>841</start_idx>
      <end_idx>950</end_idx>
      <level>2</level>
      <parent_id>results_1</parent_id>
    </section>
    <section>
      <section_id>results_1_3</section_id>
      <section_name>API Entegrasyonu</section_name>
      <content>Üçüncü parti servislerle (örneğin ödeme gateway'i) entegrasyon yaparak webhook sistemleri kuruldu. Hata yönetimi ve retry mekanizmaları implemente edildi.</content>
      <start_idx>951</start_idx>
      <end_idx>1080</end_idx>
      <level>2</level>
      <parent_id>results_1</parent_id>
    </section>
    <section>
      <section_id>conclusion_1</section_id>
      <section_name>SONUÇ VE DEĞERLENDİRME</section_name>
      <content>Bu staj deneyimi, akademik bilgilerimi pratik uygulamalara dönüştürmeme önemli katkılar sağlamıştır. Endüstriyel yazılım geliştirme süreçlerini, takım çalışmasını ve profesyonel geliştirme standartlarını yakından tanıma fırsatı buldum.

Öğrendiğim en önemli dersler şunlardır:
- Agile metodolojisinin pratik uygulaması
- Code review ve test yazma kültürü
- Production ortamında hata yönetimi

Gelecekteki kariyer planlarım için bu deneyim çok değerli olmuştur.</content>
      <start_idx>1081</start_idx>
      <end_idx>1300</end_idx>
      <level>1</level>
      <parent_id>null</parent_id>
    </section>
  </sections>
</segmentation>
```

### Format 2: JSON (Parse edilmiş)

```json
{
  "segmentation": {
    "sections": [
      {
        "section_id": "intro_1",
        "section_name": "GİRİŞ",
        "content": "Bu staj raporu, 2024 yaz döneminde [Şirket Adı] bünyesinde gerçekleştirdiğim yazılım geliştirme stajı deneyimlerimi içermektedir...",
        "start_idx": 0,
        "end_idx": 245,
        "level": 1,
        "parent_id": null
      },
      {
        "section_id": "method_1",
        "section_name": "YÖNTEM",
        "content": "Staj süresince kullanılan geliştirme metodolojisi Agile/Scrum yaklaşımına dayanmaktadır...",
        "start_idx": 246,
        "end_idx": 345,
        "level": 1,
        "parent_id": null
      },
      {
        "section_id": "method_1_1",
        "section_name": "Kullanılan Teknolojiler",
        "content": "Proje geliştirmesinde aşağıdaki teknolojiler kullanılmıştır:\n- Backend: Python 3.11, FastAPI framework...",
        "start_idx": 346,
        "end_idx": 480,
        "level": 2,
        "parent_id": "method_1"
      }
      // ... diğer bölümler
    ]
  }
}
```

---

## 🎯 Çıktının Özellikleri

### ✅ Faithful Extraction
- **İçerik %100 orijinal:** Metinden kelime değiştirilmeden, karakter karakter alıntı
- **Karakter pozisyonları doğru:** `start_idx` ve `end_idx` kaynak metindeki gerçek pozisyonları gösterir
- **Overlap yok:** Bölümler birbiriyle çakışmaz
- **Gap yok:** Tüm metin kapsanır

### ✅ Structured Output
- **Şema uyumlu:** `section.schema.json` şemasına %100 uyum
- **Gerekli alanlar:** Tüm alanlar dolu (section_id, section_name, content, start_idx, end_idx, level)
- **Hiyerarşi:** Level 1 (ana bölüm), Level 2+ (alt bölümler), parent_id ilişkileri

### ✅ Rubric'e Göre Bölüm Tanıma
- **Ana bölümler (Level 1):** Cover, Executive Summary, Company and Sector, Activity Analysis / Project, Conclusion
- **Alt bölümler (Level 2):** 
  - Company and Sector altında: Overview, Organization, Production/Service, Professional and Ethical Responsibilities
  - Activity Analysis altında: Main List of Activities, Activity Analysis, Project, Daily Activities
  - Conclusion altında: Impact, Team Work, Self-directed Learning
- **Başarı oranı:** Rubric kriterlerine karşılık gelen bölümler için %90+

---

## 💻 Kullanım Örneği

```python
from llm.tools.gemini_segment import segment_text

# PDF/DOCX'ten çıkarılmış metin
text = """
GİRİŞ
Bu staj raporu...
YÖNTEM
...
"""

# Bölümleme yap
xml_output = segment_text(text)

# XML'i parse et
import xml.etree.ElementTree as ET
root = ET.fromstring(xml_output)

# Bölümleri kullan
for section in root.findall(".//section"):
    section_id = section.find("section_id").text
    section_name = section.find("section_name").text
    content = section.find("content").text
    start_idx = int(section.find("start_idx").text)
    end_idx = int(section.find("end_idx").text)
    
    print(f"{section_name} ({section_id}): {len(content)} karakter")
    print(f"Pozisyon: {start_idx}-{end_idx}")
    print()
```

---

## 📊 Örnek Çıktı İstatistikleri

**Örnek Rapor:** Kendi PDF dosyanız (data/sample_reports/ klasörüne koyun)

**Beklenen Çıktı (Rubric'e Göre):**
- Toplam bölüm sayısı: ~15-20 bölüm (notlandırma için optimize edilmiş)
  - Level 1: 5-7 bölüm (Cover, Executive Summary, Company and Sector, Activity Analysis / Project, Conclusion, References)
  - Level 2: 8-12 alt bölüm (rubric kriterlerine karşılık gelen alt bölümler)
  - Level 3: Minimal (sadece gerekliyse)
- Ortalama bölüm uzunluğu: ~150 karakter
- İşlem süresi: 2-5 saniye (Gemini API)

---

## ✅ Doğrulama (Validation)

Çıktı şu testlerden geçmeli:

```bash
# Test suite çalıştır
cd llm
pytest tests/test_faithful.py -v
```

**Test Kriterleri:**
- ✅ XML yapı geçerli
- ✅ İçerik değişikliği yok (faithful extraction)
- ✅ İndeksler doğru (±5 karakter tolerans)
- ✅ Bölümler örtüşmüyor
- ✅ Tüm metin kapsanıyor
- ✅ Hiyerarşi doğru

---

## 📈 Hafta 2'ye Geçiş

Hafta 1 çıktısı ile hafta 2'de yapılacaklar:

1. ✅ Bölümleme çıktısı hazır → Puanlayıcı modülüne girdi olarak kullanılacak
2. ✅ Structured output mevcut → Backend API'ye entegre edilecek
3. ✅ Test suite hazır → CI/CD pipeline'a eklenecek
4. ✅ Örnek veriler var → Gerçek testler yapılacak

---

## 🎓 Özet

**Hafta 1 sonunda elimizde:**
- ✅ Çalışan bir bölümleme fonksiyonu
- ✅ XML formatında structured output
- ✅ Faithful extraction garantisi
- ✅ Test suite ve dokümantasyon
- ✅ Örnek veriler ve demo scriptleri

**Çıktı kullanıma hazır!** Hafta 2'de bu çıktı puanlayıcı modüle girdi olarak verilecek.

