# KrishiMitra AI – Complete Kerala Agriculture Scheme Intelligence & Automated Data Collection System

A production-grade, automated agricultural government scheme intelligence, document harvesting, indexing, and AI advisory platform tailored specifically for farmers in Kerala, India.

---

## 🌟 Executive Highlights

1. **Comprehensive Kerala & Central Government Coverage**:
   - Covers all **62 Kerala Government departments** listed in the Integrated Government Online Directory (IGOD), plus statutory boards (Rubber, Coconut, Spices, Coffee, NABARD), and Central Government agriculture schemes applicable to Kerala (PM-KISAN, PMFBY, MISS/KCC, MIDH, RKVY, AIF, PM-KUSUM, Soil Health Card).
   - Real-time **Scheme Coverage Matrix** tracking exact statuses (`Verified`, `Documents collected`, `Investigating`, `No relevant schemes found`).
2. **Resilient Python Government Web Crawler**:
   - `GovernmentSession` with `GovernmentTLSAdapter` supporting legacy DH ciphers (`SECLEVEL=1`) and custom state NIC CA certificates.
   - Discovers official PDFs, circulars, Government Orders (G.O.), application forms, and notifications in Malayalam and English.
   - Tested live against official portals; discovered **105+ real documents** from Karshika Keralam in a single crawl cycle.
3. **Automated Document Management & Deduplication**:
   - SHA-256 cryptographic hashing to prevent duplicate downloads and save bandwidth.
   - Automatic version tracking (`document_versions`) when government orders are superseded or modified.
4. **PDF & Malayalam OCR Processing**:
   - Multi-page extraction with PyMuPDF (`fitz`), preserving page numbers, section headers, and structured tables.
   - Integrated Tesseract Malayalam + English OCR pipeline for scanned orders.
5. **AI Scheme Information Extractor**:
   - Structured JSON schema enforcing 28+ fields, page citations, null defaults (zero hallucination rule), and conflict detection.
6. **PostgreSQL 18 + pgvector Central Database**:
   - Live connected to Neon PostgreSQL 18 with active `vector` extension.
   - 15 relational tables: `government_departments`, `government_sources`, `schemes`, `scheme_eligibility`, `scheme_benefits`, `scheme_documents`, `document_versions`, `extracted_document_content`, `scheme_amendments`, `scheme_districts`, `scheme_crops`, `farmer_profiles`, `application_guidelines`, `verification_history`, `crawler_logs`.
7. **Bilingual RAG AI Farmer Assistant**:
   - Answers questions in Malayalam and English with mandatory citations (Scheme Name, Eligibility, Benefits, Required Documents, Application Instructions, Portal URL, Source Document, Page Number, Verification Date).
8. **Rule-Based Farmer Eligibility Checker**:
   - Instant calculation across all 14 Kerala districts, landholding size, crop types, and farmer categories.
9. **Full-Stack Web Application**:
   - **Farmer Portal (`/`)**: Mobile-first, vibrant Kerala emerald aesthetic, Web Speech API voice search, crop filter pills, instant eligibility checker, and AI chatbot.
   - **Admin Studio (`/admin-portal/`)**: 6 live KPI metric cards, complete 62-department Scheme Coverage Matrix, live crawl trigger, and document explorer.

---

## 📂 System Architecture

```
krishimitra-ai/
├── core/
│   ├── config.py                 # Environment variables, DB connection, settings
│   ├── logger.py                 # Structured ISO logging to console & krishimitra.log
│   └── database.py               # Neon PostgreSQL connection pool & 15-table DDL schema
├── registry/
│   ├── models.py                 # Department & Scheme Coverage models & Enums
│   ├── departments_data.py       # Full catalog of 62 Kerala IGOD departments & Central agencies
│   ├── source_registry.py        # Registry engine syncing to PostgreSQL
│   └── coverage_matrix.py        # Real-time Scheme Coverage Matrix calculator
├── crawler/
│   ├── session.py                # Resilient GovernmentSession (Weak DH, custom CAs, retries)
│   ├── keywords.py               # Bilingual English & Malayalam keywords
│   ├── base_crawler.py           # Base crawler, robots.txt validator, document detector
│   ├── general_crawler.py        # Recursive portal crawler for all Kerala departments
│   ├── adapters/
│   │   ├── kerala_agri_adapter.py    # Adapter for Karshika Keralam (keralaagriculture.gov.in)
│   │   ├── aims_adapter.py           # Adapter for AIMS Kerala (aimsnew.kerala.gov.in)
│   │   ├── commodity_boards_adapter.py # Rubber, Coconut, Spices Boards
│   │   └── central_schemes_adapter.py  # PM-KISAN, PMFBY, MIDH, AIF
│   └── discovery_engine.py       # Orchestrator logging crawl runs into crawler_logs
├── document_manager/
│   ├── models.py                 # Download metadata & versioning models
│   ├── storage.py                # Isolated, versioned file storage
│   └── downloader.py             # SHA-256 deduplicator & version change detector
├── parser/
│   ├── models.py                 # ExtractedPage, ExtractedTable, ExtractedDocument
│   ├── normalizer.py             # Unicode Malayalam normalizer & language detector
│   ├── ocr_engine.py             # Tesseract Malayalam + English OCR adapter
│   └── pdf_extractor.py          # PyMuPDF extractor with table detection
├── ai_extractor/
│   ├── schemas.py                # Strict 28-field Pydantic schema with citations
│   ├── conflict_detector.py      # Detects conflicts in subsidies, deadlines, & orders
│   └── extractor.py              # Gemini LLM + domain heuristic extractor
├── rag/
│   ├── embeddings.py             # 1536-dim vector embedding generator
│   ├── vector_store.py           # pgvector cosine similarity search
│   └── assistant.py              # Bilingual Farmer Assistant with strict citations
├── eligibility/
│   ├── models.py                 # FarmerInputProfile & SchemeEligibilityMatch
│   └── checker.py                # Single-query aggregated eligibility evaluator
├── scheduler/
│   ├── celery_app.py             # Celery Beat cron configuration
│   ├── tasks.py                  # Health check, circular discovery, & retry tasks
│   └── standalone_runner.py      # Windows standalone runner without Redis dependency
├── web/
│   ├── settings.py               # Django settings
│   ├── urls.py                   # URLs: /, /admin-portal/, /api/...
│   ├── views.py                  # Views & REST APIs
│   ├── static/
│   │   ├── css/app.css           # Premium Kerala emerald & glassmorphism styling
│   │   └── js/farmer.js          # Voice input, bilingual state, eligibility & chat
│   └── templates/
│       ├── base.html             # Common responsive layout
│       ├── farmer.html           # Farmer-facing mobile portal
│       └── admin.html            # Admin dashboard with 62-department coverage
├── tests/
│   ├── test_download_dedup.py    # Stage 3 test
│   ├── test_pdf_extractor.py     # Stage 4 test
│   ├── test_extractor.py         # Stage 5 test
│   ├── test_rag_assistant.py     # Stage 7 test
│   └── test_eligibility.py       # Stage 8 test
├── scripts/
│   ├── inspect_sources.py        # Probes all 29 official websites for accessibility
│   ├── seed_initial_schemes.py   # Seeds baseline schemes (Paddy Royalty, PM-KISAN, Spices)
│   └── generate_coverage_report.py
├── COVERAGE_REPORT.md            # Detailed Scheme Coverage Matrix
├── requirements.txt
└── .env
```

---

## 🚀 Quickstart & Windows Execution Guide

### 1. Prerequisites
- Python 3.11+
- Neon PostgreSQL connection string (configured in `.env`)

### 2. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Initialize Database & Seed Baseline Schemes
```powershell
# Initialize all 15 PostgreSQL tables & pgvector extension
python -c "from core.database import init_db; init_db()"

# Sync 82 departments and agencies into database
python -c "from registry.source_registry import SourceRegistry; SourceRegistry().sync_to_database()"

# Seed verified initial schemes (Paddy Royalty, PM-KISAN, Spices Board, Coconut Board, Pension)
python scripts/seed_initial_schemes.py
```

### 4. Run Crawler & Discover Real Documents
```powershell
# Crawl Karshika Keralam (discovers 100+ documents live)
python -c "from crawler.discovery_engine import DiscoveryEngine; DiscoveryEngine().run_department_crawl('KL_AGRI_DEPT')"
```

### 5. Launch the Web Application
```powershell
# Start KrishiMitra AI web server on port 8080
python web/manage.py runserver 127.0.0.1:8080
```
- **Farmer Portal**: `http://127.0.0.1:8080/`
- **Admin Studio**: `http://127.0.0.1:8080/admin-portal/`
- **Coverage Matrix API**: `http://127.0.0.1:8080/api/coverage/matrix/`
- **Schemes API**: `http://127.0.0.1:8080/api/schemes/`

---

## 🧪 Verified Test Suite

Run individual stage verification tests:
```powershell
# Test Stage 3: Download and SHA-256 deduplication
python tests/test_download_dedup.py

# Test Stage 4: PyMuPDF PDF and table extraction
python tests/test_pdf_extractor.py

# Test Stage 5: AI Scheme Information Extraction
python tests/test_extractor.py

# Test Stage 7: Bilingual RAG Farmer Assistant with citations
python tests/test_rag_assistant.py

# Test Stage 8: Farmer Eligibility Checker (Wayanad, Palakkad, etc.)
python tests/test_eligibility.py
```
