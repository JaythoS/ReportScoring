# 🚀 Hızlı Başlangıç - Canlı Demo

## 1️⃣ Paketleri Yükle

```bash
cd /Users/helindincel/bitirme2
pip install google-generativeai
```

## 2️⃣ API Key'i Ayarla

Terminal'de şu komutu çalıştırın (API key'inizi yazın):

```bash
export GEMINI_API_KEY="AIzaSyApKiQQMhbBVZ1rkGSYwlwfhC..."
```

**API Key almak için:** https://aistudio.google.com/app/apikey

## 3️⃣ Demo'yu Çalıştır

```bash
python llm/tools/demo_live.py
```

## 🎯 Farklı Raporlar İçin

```bash
# Türkçe rapor
python llm/tools/demo_live.py --report 1

# İngilizce rapor
python llm/tools/demo_live.py --report 2

# Karışık format
python llm/tools/demo_live.py --report 3
```

## ⚡ API Key'i Komut Satırında Direkt Verme

API key'i environment variable'a ayarlamak istemiyorsanız:

```bash
python llm/tools/demo_live.py --api-key "AIzaSyApKiQQMhbBVZ1rkGSYwlwfhC..."
```

## 📋 Beklenen Çıktı (Rubric-Based)

Demo çalıştığında:
- ✅ Rubric kriterlerine göre bölüm sayısı gösterilir (~15-20 bölüm)
- ✅ Her bölüm için: ID, ad, seviye, pozisyon bilgileri
- ✅ İçerik önizlemesi
- ✅ JSON çıktısı (rubric'e göre yapılandırılmış)
- ✅ Hiyerarşi doğruluğu (Impact, Team Work, Self-directed Learning → Level 2)

## ❌ Sorun Giderme

**"ModuleNotFoundError: No module named 'google.generativeai'"**
→ `pip install google-generativeai` çalıştırın

**"GEMINI_API_KEY bulunamadı"**
→ Terminal'de `export GEMINI_API_KEY="..."` komutunu çalıştırın

**"API key invalid"**
→ API key'inizi kontrol edin: https://aistudio.google.com/app/apikey

