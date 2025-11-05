# 🎓 Staj Raporu Otomatik Değerlendirme Sistemi - Proje Dokümantasyonu

**Teknoloji:** Python FastAPI + PostgreSQL + Streamlit  

---

## 📋 İçindekiler

1. [Proje Genel Bakış](#1-proje-genel-bakış)
2. [Sistem Mimarisi](#2-sistem-mimarisi)
3. [Backend File Structure](#3-backend-file-structure)
4. [Analysis Pipeline ve Örnek Çıktılar](#4-analysis-pipeline-ve-örnek-çıktılar)
5. [Database Yapısı](#5-database-yapısı)
6. [API Endpoints](#6-api-endpoints)
7. [Veri Akışı](#7-veri-akışı)

---

## 1. Proje Genel Bakış

### 1.1 Amaç

Öğrencilerin yüklediği staj raporlarını (PDF/DOCX) **otomatik olarak analiz edip**, belirlenen rubrik kriterlerine göre **puanlayan** ve **detaylı geri bildirim** sağlayan bir web uygulaması.

### 1.2 Ana İşlevler

1. **Dosya Yükleme** - PDF/DOCX formatında staj raporu yükleme
2. **Otomatik Bölümleme** - LLM ile raporu bölümlere ayırma
3. **Çoklu Kriter Puanlama** - 9 rubrik kriteri için ayrı puan hesaplama
4. **Kanıt Tabanlı Geri Bildirim** - Metinden alıntılarla puanları destekleme
5. **Ağırlıklı Toplam Puan** - Tüm kriterlerin ağırlıklı ortalaması
6. **Görselleştirme** - Sonuçları tablo ve grafiklerle gösterme

### 1.3 Teknoloji Stack

**Backend:** Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy, OpenAI/Claude API  
**Frontend:** Streamlit, Pandas, Plotly  
**Infrastructure:** Docker, Docker Compose, Alembic

---

## 2. Sistem Mimarisi

### 2.1 Genel Mimari Diyagramı

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Streamlit)                      │
│  ┌────────────┬──────────────┬────────────┬───────────────┐ │
│  │   Upload   │   Preview    │  Progress  │    Results    │ │
│  │   Page     │   Component  │    Bar     │    Table      │ │
│  └────────────┴──────────────┴────────────┴───────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API (HTTP/JSON)
┌───────────────────────────▼─────────────────────────────────┐
│                  BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            API Layer (Routes)                         │   │
│  │  POST /upload      GET /results/{report_id}         │   │
│  └────────────────────────┬─────────────────────────────┘   │
│  ┌────────────────────────▼─────────────────────────────┐   │
│  │         Analysis Pipeline (Senkron)                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────┐  │   │
│  │  │    File    │→ │    LLM     │→ │    LLM      │  │   │
│  │  │   Parser   │  │Integration │  │ Integration │  │   │
│  │  │            │  │  (Section  │  │  (Scorer)   │  │   │
│  │  │            │  │  Splitter) │  │             │  │   │
│  │  └────────────┘  └────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
┌───────────────────────────▼─────────────────────────────────┐
│               DATABASE (PostgreSQL)                          │
│  ┌────────┬──────────┬────────┬──────────┬────────────┐    │
│  │Reports │ Sections │ Scores │ Evidence │Suggestions │    │
│  │        │          │        │          │ & Issues   │    │
│  └────────┴──────────┴────────┴──────────┴────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Veri Akışı

```
[Öğrenci]
    │
    └─ 1. PDF/DOCX yükle
       ▼
[Frontend: Upload]
    │
    └─ 2. POST /api/v1/upload
       ▼
[Backend: Upload Handler]
    │
    ├─ 3. Dosyayı kaydet
    ├─ 4. Report DB'ye yaz
    └─ 5. PIPELINE BAŞLA (senkron)
       ▼
[File Parser]
    │
    └─ 6. PDF/DOCX → Metin çıkar
       ▼
[LLM Integration: Section Splitter]
    │
    ├─ 7. Metni bölümlere ayır
    └─ 8. Sections DB'ye yaz
       ▼
[LLM Integration: Scorer Engine]
    │
    ├─ 9. Her bölüm için puan hesapla
    └─ 10. Scores, Evidence, Issues, Suggestions DB'ye yaz
       ▼
[Response]
    │
    └─ 11. Sonucu döndür
       ▼
[Frontend]
    │
    └─ 12. Sonucu göster (tablo, grafikler)
```

---

## 3. Backend File Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app, CORS, startup/shutdown
│   ├── config.py                    # Environment variables, constants
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                  # Dependencies (get_db)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── upload.py        # POST /upload
│   │       │   ├── results.py       # GET /results/{report_id}
│   │       │   └── reports.py       # GET /reports, DELETE /reports/{id}
│   │       └── router.py            # API router (tüm endpoint'leri toplar)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py              # Database connection, SessionLocal
│   │   └── exceptions.py            # Custom exception classes
│   │
│   ├── models/                      # SQLAlchemy models (Database tables)
│   │   ├── __init__.py
│   │   ├── report.py
│   │   ├── section.py
│   │   ├── score.py
│   │   ├── evidence.py
│   │   ├── suggestion.py
│   │   └── issue.py
│   │
│   ├── schemas/                     # Pydantic schemas (API request/response)
│   │   ├── __init__.py
│   │   ├── report.py
│   │   ├── section.py
│   │   ├── score.py
│   │   ├── upload.py
│   │   └── common.py
│   │
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── file_handler.py          # File saving, validation
│   │   ├── file_parser.py           # PDF/DOCX → text extraction
│   │   ├── llm_integration.py       # LLM API calls
│   │   ├── section_splitter.py      # LLM-based section splitting
│   │   ├── scorer.py                # LLM-based scoring
│   │   └── analysis_pipeline.py     # Main pipeline orchestration
│   │
│   └── constants/
│       ├── __init__.py
│       └── rubric.py                # Rubric definitions (9 criteria)
│
├── alembic/                         # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 3.1 Dosya Açıklamaları

| Dosya/Klasör | Açıklama |
|--------------|----------|
| `app/main.py` | FastAPI app, CORS, router mounting, exception handlers |
| `app/config.py` | Environment variables (DATABASE_URL, OPENAI_API_KEY, vb.) |
| `app/api/deps.py` | Dependency injection (get_db function) |
| `app/api/v1/router.py` | Tüm endpoint'leri toplar, versiyonlama |
| `app/core/database.py` | SQLAlchemy engine, SessionLocal, Base |
| `app/core/exceptions.py` | Custom exceptions (FileTooLargeError, LLMAPIError, vb.) |
| `app/models/*.py` | SQLAlchemy models (Database tabloları) |
| `app/schemas/*.py` | Pydantic schemas (API request/response) |
| `app/services/*.py` | Business logic (file parsing, LLM, pipeline) |
| `app/constants/rubric.py` | 9 rubrik kriterinin tanımları |
| `alembic/` | Database migration yönetimi |

---

## 4. Analysis Pipeline ve Örnek Çıktılar

### 4.1 Pipeline Adımları

```
┌─────────────────────────────────────────────────────────────┐
│                   ANALYSIS PIPELINE                          │
│                                                              │
│  Step 1: File Parser                                        │
│  Input:  ahmet_yilmaz_staj_raporu.pdf                      │
│  Output: full_text (string)                                 │
│                                                              │
│  Step 2: LLM Integration - Section Splitter                 │
│  Input:  full_text                                          │
│  Output: sections (list of dict)                            │
│                                                              │
│  Step 3: LLM Integration - Scorer Engine                    │
│  Input:  sections + full_text                               │
│  Output: scores + evidence + issues + suggestions           │
│                                                              │
│  Step 4: Database Save                                      │
│  Save:   Report, Sections, Scores, Evidence, etc.          │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Adım 1: File Parser - Çıktı

```json
{
  "full_text": "STAJ RAPORU\n\nExecutive Summary\nBu stajda ABC Firmasında çalıştım...\n\nActivity Analysis\nÜretim verimliliği %15 arttı...",
  "page_count": 12,
  "word_count": 3458,
  "metadata": {
    "filename": "staj_raporu_2024.pdf",
    "file_size": 5242880,
    "parsed_at": "2025-11-05T14:23:11Z"
  }
}
```

### 4.3 Adım 2: Section Splitter - Çıktı

```json
{
  "sections": [
    {
      "name": "Executive Summary",
      "start_index": 87,
      "end_index": 412,
      "content": "Bu stajda ABC Firmasında çalıştım...",
      "page_number": 1,
      "word_count": 47
    },
    {
      "name": "Activity Analysis",
      "start_index": 995,
      "end_index": 1856,
      "content": "Üretim verimliliği %15 arttı...",
      "page_number": 5,
      "word_count": 134
    }
  ]
}
```

### 4.4 Adım 3: Scorer Engine - Çıktı

```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_score": 78.4,
  "processing_time_seconds": 145.7,
  
  "criterion_scores": [
    {
      "criterion_name": "Executive Summary",
      "criterion_weight": 0.06,
      "raw_score": 75.0,
      "calibrated_score": 73.2,
      "weighted_contribution": 4.39,
      
      "evidence": [
        "Sayfa 1: 'Bu stajda ABC Firmasında çalıştım'",
        "Sayfa 1: 'Stajın amacı üretim süreçlerini analiz etmekti'"
      ],
      
      "issues": [
        "Şirketin ana faaliyetleri detaylı anlatılmamış"
      ],
      
      "suggestions": [
        "Şirketin hangi ürünleri ürettiğini ekleyin"
      ]
    },
    {
      "criterion_name": "Activity Analysis",
      "criterion_weight": 0.40,
      "raw_score": 88.0,
      "calibrated_score": 86.5,
      "weighted_contribution": 34.60,
      
      "evidence": [
        "Sayfa 5: 'Üretim verimliliği %15 arttı'",
        "Sayfa 5: 'Aylık maliyet 8000 TL azaldı'"
      ],
      
      "issues": [
        "İstatistiksel analiz yöntemleri detaylandırılmamış"
      ],
      
      "suggestions": [
        "Kullandığınız testleri belirtin (T-testi, ANOVA)"
      ]
    }
  ],
  
  "sections_found": [
    {"name": "Executive Summary", "page": 1, "word_count": 47},
    {"name": "Activity Analysis", "page": 5, "word_count": 134}
  ],
  
  "model_info": {
    "model_name": "gpt-4-turbo",
    "model_version": "2024-04-09"
  }
}
```

---

## 5. Database Yapısı

### 5.1 ERD (Entity Relationship Diagram)

```
                           REPORTS
                    ┌──────────────────┐
                    │ id (PK)          │
                    │ filename         │
                    │ file_type        │
                    │ file_size        │
                    │ file_path        │
                    │ uploaded_at      │
                    │ error_message    │
                    │ metadata         │
                    └────────┬─────────┘
                             │ 1:N
                    ┌────────▼─────────┐
                    │    SECTIONS      │
                    │ id (PK)          │
                    │ report_id (FK)   │
                    │ name             │
                    │ content          │
                    │ start_index      │
                    │ end_index        │
                    │ page_number      │
                    │ word_count       │
                    │ extracted_at     │
                    └────────┬─────────┘
                             │ 1:N
                    ┌────────▼─────────┐
                    │     SCORES       │
                    │ id (PK)          │
                    │ report_id (FK)   │
                    │ section_id (FK)  │
                    │ criterion_name   │
                    │ criterion_weight │
                    │ raw_score        │
                    │ calibrated_score │
                    │ scored_at        │
                    │ model_version    │
                    └────────┬─────────┘
                             │ 1:N
        ┌────────────────────┼────────────────────┐
        │                    │                    │
  ┌─────▼──────┐   ┌─────────▼────┐   ┌──────────▼─────┐
  │  EVIDENCE  │   │ SUGGESTIONS  │   │    ISSUES      │
  │ id (PK)    │   │ id (PK)      │   │ id (PK)        │
  │ score_id   │   │ score_id     │   │ score_id       │
  │ text       │   │ text         │   │ text           │
  │ page_number│   └──────────────┘   └────────────────┘
  │ start_char │
  │ end_char   │
  └────────────┘
```

### 5.2 Tablo Açıklamaları

**REPORTS** (Ana Rapor Tablosu)
- `id`: UUID, Primary Key
- `filename`: Dosya adı (örn: "staj_raporu_2024.pdf")
- `file_type`: Dosya formatı ("pdf" veya "docx")
- `file_size`: Dosya boyutu (bytes)
- `file_path`: Sunucudaki dosya yolu
- `uploaded_at`: Yüklenme zamanı
- `error_message`: Hata mesajı (varsa)
- `metadata`: Ek bilgiler (JSONB)

**SECTIONS** (Rapor Bölümleri)
- `id`: UUID, Primary Key
- `report_id`: Foreign Key → reports.id
- `name`: Bölüm adı ("Executive Summary", "Activity Analysis", vb.)
- `content`: Bölümün tam metni
- `start_index`: Metinde başlangıç karakter pozisyonu
- `end_index`: Metinde bitiş karakter pozisyonu
- `page_number`: Sayfa numarası
- `word_count`: Kelime sayısı
- `extracted_at`: Çıkarılma zamanı

**SCORES** (Puanlar)
- `id`: UUID, Primary Key
- `report_id`: Foreign Key → reports.id
- `section_id`: Foreign Key → sections.id (nullable)
- `criterion_name`: Kriter adı ("Executive Summary", vb.)
- `criterion_weight`: Ağırlık (0.06, 0.40, vb.)
- `raw_score`: Ham puan (0-100)
- `calibrated_score`: Kalibre edilmiş puan
- `scored_at`: Puanlama zamanı
- `model_version`: Kullanılan LLM modeli

**EVIDENCE** (Kanıtlar)
- `id`: UUID, Primary Key
- `score_id`: Foreign Key → scores.id
- `evidence_text`: Kanıt metni (alıntı)
- `page_number`: Sayfa numarası
- `start_char`: Başlangıç karakter pozisyonu
- `end_char`: Bitiş karakter pozisyonu

**SUGGESTIONS** (Öneriler)
- `id`: UUID, Primary Key
- `score_id`: Foreign Key → scores.id
- `suggestion_text`: Öneri metni

**ISSUES** (Sorunlar)
- `id`: UUID, Primary Key
- `score_id`: Foreign Key → scores.id
- `issue_text`: Sorun metni

---

## 6. API Endpoints

### 6.1 POST `/api/v1/upload`

**Açıklama:** Rapor yükle ve senkron olarak analiz et

**Request:**
```http
POST /api/v1/upload HTTP/1.1
Content-Type: multipart/form-data

file: <binary>
```

**Response (200 OK):**
```json
{
  "status": "completed",
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Rapor başarıyla analiz edildi",
  "processing_time_seconds": 145.7,
  
  "results": {
    "total_score": 78.4,
    
    "criterion_scores": [
      {
        "criterion_name": "Executive Summary",
        "weight": 0.06,
        "raw_score": 75.0,
        "calibrated_score": 73.2,
        "weighted_contribution": 4.39,
        "evidence": ["Sayfa 1: ..."],
        "issues": ["..."],
        "suggestions": ["..."]
      }
    ],
    
    "sections_found": [
      {"name": "Executive Summary", "page": 1, "word_count": 47}
    ],
    
    "model_info": {
      "model_name": "gpt-4-turbo",
      "model_version": "2024-04-09"
    }
  }
}
```

**Error (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_FORMAT",
    "message": "Desteklenmeyen dosya formatı",
    "details": {
      "allowed_formats": ["pdf", "docx"],
      "received_format": "txt"
    }
  }
}
```

**Error (413 Payload Too Large):**
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "Dosya boyutu limiti aşıldı",
    "details": {
      "max_size_mb": 15,
      "uploaded_size_mb": 23.5
    }
  }
}
```

---

### 6.2 GET `/api/v1/results/{report_id}`

**Açıklama:** Mevcut rapor sonuçlarını getir

**Request:**
```http
GET /api/v1/results/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
```

**Response (200 OK):**
```json
{
  "status": "completed",
  "report": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "staj_raporu_2024.pdf",
    "uploaded_at": "2025-11-05T14:23:11Z"
  },
  "results": {
    "total_score": 78.4,
    "criterion_scores": [...]
  }
}
```

**Error (404 Not Found):**
```json
{
  "error": {
    "code": "REPORT_NOT_FOUND",
    "message": "Belirtilen report_id bulunamadı"
  }
}
```

---

### 6.3 GET `/api/v1/reports`

**Açıklama:** Tüm raporları listele

**Request:**
```http
GET /api/v1/reports?limit=10&offset=0 HTTP/1.1
```

**Response (200 OK):**
```json
{
  "reports": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "staj_raporu_2024.pdf",
      "uploaded_at": "2025-11-05T14:23:11Z",
      "total_score": 78.4
    }
  ],
  "pagination": {
    "total": 47,
    "limit": 10,
    "offset": 0
  }
}
```

---

### 6.4 DELETE `/api/v1/reports/{report_id}`

**Açıklama:** Raporu ve ilgili tüm verileri sil

**Request:**
```http
DELETE /api/v1/reports/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
```

**Response (200 OK):**
```json
{
  "message": "Rapor ve ilgili veriler başarıyla silindi",
  "deleted_report_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 7. Veri Akışı

### 7.1 Tam Akış Diyagramı

```
┌─────────────┐
│  FRONTEND   │
└──────┬──────┘
       │ POST /api/v1/upload
       ▼
┌──────────────────────────────────────┐
│  SCHEMA (Pydantic Validation)       │
│  Request'i validate et               │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  ENDPOINT (Business Logic)           │
│  - Dosya kaydet                      │
│  - Pipeline çalıştır                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  MODEL (SQLAlchemy)                  │
│  Database'e kaydet                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  POSTGRESQL DATABASE                 │
│  Veri saklandı                       │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  ANALYSIS PIPELINE                   │
│  Analiz tamamlandı                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  MODEL (Database Read)               │
│  Sonuçları oku                       │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  SCHEMA (Response Format)            │
│  JSON formatına çevir                │
└──────┬───────────────────────────────┘
       │
       ▼
┌─────────────┐
│  FRONTEND   │
│  Göster     │
└─────────────┘
```

### 7.2 Özet

```
Frontend 
  → Schema (Request Validation)
  → Endpoint (Business Logic)
  → Model (Database Write)
  → PostgreSQL
  → Analysis Pipeline
  → Model (Database Read)
  → Schema (Response Format)
  → Frontend
```

---

