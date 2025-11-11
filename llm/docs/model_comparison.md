# LLM Model Karşılaştırması

## Staj Raporu Bölümleme için Model Seçimi

### Değerlendirme Kriterleri

1. **Faithful Extraction Yeteneği**: Metni değiştirmeden, karakter-pozisyonlu alıntı yapabilme
2. **Structured Output Desteği**: XML/JSON şema uyumlu çıktı üretme
3. **Türkçe/İngilizce Destek**: Her iki dilde de başarılı performans
4. **Maliyet**: API maliyeti ve kullanım limitleri
5. **Hız**: Yanıt süresi (latency)
6. **Güvenilirlik**: Hallucination oranı, şema ihlalleri

---

## Model Seçenekleri

### 1. Google Gemini 1.5 Flash (Önerilen ✅)

**Artıları:**
- XML structured output desteği (`response_mime_type: application/xml`)
- Türkçe ve İngilizce'de güçlü performans
- Düşük maliyet (Flash modeli)
- Hızlı yanıt süresi (~1-2 saniye)
- Güvenilir şema uyumu

**Eksileri:**
- API key gereksinimi
- İnternet bağımlılığı

**Kullanım Senaryosu:**
- Varsayılan model olarak kullanılacak
- Production ortamında tercih edilir

**Maliyet:** ~$0.075 / 1M input tokens, $0.30 / 1M output tokens

---

### 2. OpenAI GPT-4o / GPT-4o-mini

**Artıları:**
- Mükemmel Türkçe/İngilizce performans
- JSON Mode desteği (structured output)
- Yüksek doğruluk

**Eksileri:**
- XML desteği sınırlı (JSON daha iyi)
- Daha yüksek maliyet (GPT-4o)
- Rate limiting daha sıkı

**Kullanım Senaryosu:**
- Fallback model (Gemini başarısız olursa)
- JSON çıktı formatına geçiş gerekirse

**Maliyet:** 
- GPT-4o: ~$5.00 / 1M input, $15.00 / 1M output
- GPT-4o-mini: ~$0.15 / 1M input, $0.60 / 1M output

---

### 3. Anthropic Claude 3.5 Sonnet / Haiku

**Artıları:**
- İyi structured output desteği
- Düşük hallucination oranı
- JSON şema desteği

**Eksileri:**
- XML desteği zayıf
- Türkçe desteği Gemini'den daha zayıf olabilir
- Maliyet orta seviye

**Kullanım Senaryosu:**
- Alternatif JSON-based pipeline için
- Çoklu model değerlendirmesi için

**Maliyet:**
- Sonnet: ~$3.00 / 1M input, $15.00 / 1M output
- Haiku: ~$0.25 / 1M input, $1.25 / 1M output

---

### 4. Açık Kaynak Modeller (OSS 20B+)

#### 4.1. Llama 3.1 70B / 8B

**Artıları:**
- Açık kaynak, özelleştirilebilir
- Yerel çalıştırılabilir (maliyet yok)
- Özel fine-tuning yapılabilir

**Eksileri:**
- Hardware gereksinimi (GPU)
- Türkçe performansı sınırlı olabilir
- XML structured output için ek mühendislik gerekir
- Kurulum ve bakım karmaşıklığı

**Kullanım Senaryosu:**
- Test/development ortamı
- Veri gizliliği kritikse
- Uzun vadeli özelleştirme için

**Gereksinimler:**
- Minimum: 1x A100 40GB veya eşdeğeri
- Önerilen: 2x A100 80GB

#### 4.2. Mistral Large / Medium

**Artıları:**
- İyi performans/ölçek dengesi
- Açık kaynak seçenekler mevcut

**Eksileri:**
- Türkçe desteği sınırlı
- Structured output için ek geliştirme gerekir

---

## Karşılaştırma Tablosu

| Model | XML Desteği | Türkçe | Maliyet | Hız | Güvenilirlik | Önerilen Kullanım |
|-------|-------------|--------|---------|-----|--------------|-------------------|
| Gemini 1.5 Flash | ✅ Mükemmel | ✅ Çok İyi | 💰💰 Düşük | ⚡⚡⚡ Hızlı | ⭐⭐⭐⭐ | **Varsayılan** |
| GPT-4o-mini | ⚠️ JSON (XML sınırlı) | ✅ Mükemmel | 💰💰 Orta | ⚡⚡ Hızlı | ⭐⭐⭐⭐⭐ | Fallback |
| Claude 3.5 Haiku | ⚠️ JSON (XML sınırlı) | ✅ İyi | 💰💰 Orta | ⚡⚡⚡ Hızlı | ⭐⭐⭐⭐ | Alternatif |
| Llama 3.1 70B | ❌ Geliştirme gerekir | ⚠️ Orta | 💰💰💰 Yerel (GPU) | ⚡ Yavaş | ⭐⭐⭐ | Test/Development |

---

## Önerilen Strateji

### Hafta 1-3: Development
- **Birincil**: Gemini 1.5 Flash (XML structured output)
- **Fallback**: GPT-4o-mini (JSON formatına çevrilerek)

### Hafta 4-7: Production v0
- **Birincil**: Gemini 1.5 Flash
- **A/B Test**: GPT-4o-mini ile karşılaştırma

### Hafta 8-10: Optimizasyon
- Model performans metrikleri toplama
- En iyi model seçimi
- OSS model denemeleri (isteğe bağlı)

---

## İmplementasyon Notları

### Gemini Kullanımı
```python
model = genai.GenerativeModel(
    "gemini-1.5-flash-latest",
    generation_config={
        "temperature": 0,  # Deterministik çıktı
        "response_mime_type": "application/xml"  # XML zorunlu
    }
)
```

### GPT-4o-mini Fallback
- JSON çıktı formatı kullanılır
- XML'e dönüştürme post-processing ile yapılır

### OSS Model Kurulumu
- Ollama veya vLLM ile yerel deployment
- Structured output için özel prompt engineering
- Türkçe performans için fine-tuning gerekebilir

---

## Sonuç

**Önerilen Model: Google Gemini 1.5 Flash**
- XML structured output ile doğrudan uyum
- Düşük maliyet ve hızlı yanıt
- Türkçe/İngilizce güçlü destek
- Production-ready

**Fallback Planı:**
- Gemini başarısız olursa → GPT-4o-mini (JSON mode)
- Rate limit → Bekleme + retry mekanizması

