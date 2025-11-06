# 🔧 API Key Sorun Giderme

## ❌ "API key not valid" Hatası

Bu hatayı alıyorsanız:

### 1. API Key'i Kontrol Edin

**Yaygın sorunlar:**
- ✅ API key başında/sonunda gereksiz boşluk var mı?
- ✅ API key tamamen kopyalandı mı? (eksik karakter olmamalı)
- ✅ API key aktif mi? (süresi dolmuş olabilir)

### 2. API Key'i Test Edin

```bash
python llm/tools/test_api_key.py --key "AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"
```

Bu script API key'in geçerli olup olmadığını kontrol eder.

### 3. Yeni API Key Alın

Eğer key geçersizse:

1. **Google AI Studio'ya gidin:** https://aistudio.google.com/app/apikey
2. Mevcut key'i silin (veya yeni bir tane oluşturun)
3. Yeni key'i kopyalayın
4. Terminal'de ayarlayın:
   ```bash
   export GEMINI_API_KEY="AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"
   ```
5. Tekrar test edin:
   ```bash
   python llm/tools/test_api_key.py
   ```

### 4. API Key Formatı

Geçerli bir Gemini API key şu şekilde görünür:
```
AIzaSy...uzun-bir-string...xyz123
```

- Başında `AIzaSy` ile başlar
- Yaklaşık 39 karakter uzunluğundadır
- Özel karakterler içerebilir (`-`, `_`, vb.)

---

## ⚠️ "ModuleNotFoundError: No module named 'google.generativeai'"

**Çözüm:**
```bash
pip install google-generativeai
```

---

## ⚠️ "GEMINI_API_KEY is not set"

**Çözüm 1:** Terminal'de ayarlayın
```bash
export GEMINI_API_KEY="AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"
```

**Çözüm 2:** Komut satırında direkt verin
```bash
python llm/tools/demo_live.py --api-key "AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"
```

**Çözüm 3:** .env dosyası oluşturun
```bash
echo 'GEMINI_API_KEY=your-key-here' > .env
```

---

## ⚠️ "quota exceeded" veya "rate limit"

**Açıklama:** Ücretsiz Gemini API'nin günlük limiti dolmuş olabilir.

**Çözümler:**
1. Birkaç saat bekleyin (günlük limit reset olur)
2. Farklı bir API key kullanın
3. Google Cloud Console'dan quota ayarlarınızı kontrol edin

---

## ✅ Hızlı Kontrol Listesi

1. [ ] API key doğru kopyalandı mı?
2. [ ] `export GEMINI_API_KEY="..."` komutu çalıştırıldı mı?
3. [ ] `python llm/tools/test_api_key.py` başarılı mı?
4. [ ] İnternet bağlantısı var mı?
5. [ ] `google-generativeai` paketi yüklü mü?

---

## 🆘 Hala Çalışmıyor mu?

1. **Yeni terminal açın** ve tekrar deneyin
2. **API key'i yeniden oluşturun:** https://aistudio.google.com/app/apikey
3. **Test scriptini çalıştırın:** `python llm/tools/test_api_key.py`
4. **Hata mesajını tam olarak okuyun** - genelde çözüm ipucu verir

---

## 📞 Destek

- Gemini API Dokümantasyonu: https://ai.google.dev/docs
- API Key Yönetimi: https://aistudio.google.com/app/apikey

