# API Key Kurulum Rehberi

## 🔑 Gemini API Key Nasıl Alınır?

1. **Google AI Studio'ya gidin:** https://aistudio.google.com/app/apikey
2. "Create API Key" butonuna tıklayın
3. Google hesabınızla giriş yapın
4. API key'inizi kopyalayın

---

## 📝 API Key'i Ayarlama Yöntemleri

### Yöntem 1: Environment Variable (Önerilen)

**Terminal'de (macOS/Linux):**
```bash
export GEMINI_API_KEY="AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"
```

**Kalıcı yapmak için (zsh kullanıyorsanız):**
```bash
echo 'export GEMINI_API_KEY="AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"' >> ~/.zshrc
source ~/.zshrc
```

**Terminal'de (Windows PowerShell):**
```powershell
$env:GEMINI_API_KEY="AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"
```

### Yöntem 2: Komut Satırı Argümanı

Demo çalıştırırken direkt olarak:
```bash
python llm/tools/demo_live.py --api-key "AIzaSyApKiQQMhbBVZlrkGSYwlwfhCWYrL4U7tI"
```

### Yöntem 3: .env Dosyası

1. Proje kök dizininde `.env` dosyası oluşturun:
```bash
cd /Users/helindincel/bitirme2
touch .env
```

2. `.env` dosyasına yazın:
```
GEMINI_API_KEY=your-api-key-here
```

3. Python-dotenv yükleyin (gerekirse):
```bash
pip install python-dotenv
```

**Not:** `.env` dosyası `.gitignore`'da olduğu için Git'e commit edilmez.

---

## ✅ Test Etme

### API Key'i Test Et (Önerilen)

API key'inizin geçerli olup olmadığını önce test edin:

```bash
# Environment variable ile:
export GEMINI_API_KEY="your-key-here"
python llm/tools/test_api_key.py

# Veya direkt key ile:
python llm/tools/test_api_key.py --key "your-key-here"
```

### Demo'yu Çalıştır

API key geçerliyse demo'yu çalıştırın:

```bash
# Yöntem 1 veya 3 kullandıysanız:
python llm/tools/demo_live.py

# Yöntem 2 kullandıysanız:
python llm/tools/demo_live.py --api-key "your-key"
```

---

## 🔒 Güvenlik Notları

- ⚠️ **API key'inizi ASLA Git'e commit etmeyin!**
- ⚠️ **API key'inizi başkalarıyla paylaşmayın!**
- ✅ `.env` dosyası `.gitignore`'da olduğu için güvenli
- ✅ Environment variable kullanmak en güvenli yöntem

---

## 🐛 Sorun Giderme

**"GEMINI_API_KEY is not set" hatası alıyorsanız:**

1. Terminal'de kontrol edin:
```bash
echo $GEMINI_API_KEY
```

2. Eğer boşsa, tekrar ayarlayın ve demo'yu çalıştırın.

3. Yeni bir terminal penceresi açtıysanız, environment variable'ı tekrar ayarlamanız gerekebilir.

