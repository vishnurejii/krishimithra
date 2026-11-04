"""
PostgreSQL Database Manager for KrishiMitra AI.
Handles connection management, schema initialization, and table migrations.
Includes pgvector extension support for semantic search over scheme passages.
"""

import psycopg
from psycopg.rows import dict_row
from core.config import DATABASE_URL
from core.logger import get_logger

logger = get_logger("krishimitra.database")

SCHEMA_SQL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Government Departments (Core, Allied, Rural, Local-Self Govt, Central)
CREATE TABLE IF NOT EXISTS government_departments (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    malayalam_name VARCHAR(255),
    code VARCHAR(32),
    level VARCHAR(32) NOT NULL, -- State, Central, District, Local-Self-Govt
    category VARCHAR(64) NOT NULL, -- Agriculture, Animal Husbandry, Dairy, Fisheries, etc.
    official_website VARCHAR(512),
    portal_type VARCHAR(64),
    investigation_status VARCHAR(64) DEFAULT 'NOT_INVESTIGATED',
    has_agriculture_schemes BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Government Sources (Specific websites, portals, circular pages)
CREATE TABLE IF NOT EXISTS government_sources (
    id VARCHAR(64) PRIMARY KEY,
    department_id VARCHAR(64) REFERENCES government_departments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    base_url VARCHAR(512) NOT NULL,
    scheme_listing_url VARCHAR(512),
    source_type VARCHAR(64), -- Portal, Circulars, Orders Repository, University, Board
    is_active BOOLEAN DEFAULT TRUE,
    ssl_bypass_required BOOLEAN DEFAULT FALSE,
    last_checked_at TIMESTAMPTZ,
    last_status_code INT,
    health_status VARCHAR(32) DEFAULT 'UNKNOWN', -- HEALTHY, DEGRADED, DOWN
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Schemes Master Table
CREATE TABLE IF NOT EXISTS schemes (
    id VARCHAR(64) PRIMARY KEY,
    department_id VARCHAR(64) REFERENCES government_departments(id) ON DELETE SET NULL,
    source_id VARCHAR(64) REFERENCES government_sources(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    malayalam_name VARCHAR(255),
    code VARCHAR(64),
    classification VARCHAR(64) NOT NULL, -- Scheme, Service, Subsidy, Welfare/Pension, Loan, Insurance, Training, Price Incentive
    level VARCHAR(32) NOT NULL, -- State, Central, Centrally Sponsored (CSS), District, Local-Body
    objective TEXT,
    description TEXT,
    status VARCHAR(32) DEFAULT 'VERIFICATION_PENDING', -- PROPOSED, APPROVED, ACTIVE, EXPIRED, DISCONTINUED, VERIFICATION_PENDING
    is_active BOOLEAN DEFAULT FALSE,
    official_portal_url VARCHAR(512),
    application_procedure TEXT,
    application_deadline DATE,
    financial_year VARCHAR(32),
    valid_from DATE,
    valid_until DATE,
    last_verified_at TIMESTAMPTZ,
    verification_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Scheme Eligibility Rules
CREATE TABLE IF NOT EXISTS scheme_eligibility (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE CASCADE,
    beneficiary_categories TEXT[], -- Small Farmer, Marginal Farmer, Women, Youth, SC, ST, General
    eligible_farmer_types TEXT[], -- Owner-cultivator, Tenant farmer, Kudumbashree JLG, Sharecropper
    min_land_acres NUMERIC(8, 2),
    max_land_acres NUMERIC(8, 2),
    income_limit NUMERIC(12, 2),
    caste_category VARCHAR(64),
    residency_requirements TEXT,
    other_conditions TEXT,
    exclusions TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Scheme Benefits & Subsidies
CREATE TABLE IF NOT EXISTS scheme_benefits (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE CASCADE,
    benefit_type VARCHAR(64), -- Direct Cash, Capital Subsidy, Interest Subvention, Input Subsidy, Equipment Subsidy
    subsidy_amount NUMERIC(12, 2),
    subsidy_percentage NUMERIC(5, 2),
    max_assistance_limit NUMERIC(12, 2),
    unit_of_assistance VARCHAR(128), -- per acre, per hectare, per unit, per farmer
    disbursement_mode VARCHAR(64), -- DBT, Bank Account, Kind/Inputs
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Scheme Documents (Original documents discovered & tracked)
CREATE TABLE IF NOT EXISTS scheme_documents (
    id VARCHAR(64) PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE SET NULL,
    department_id VARCHAR(64) REFERENCES government_departments(id) ON DELETE SET NULL,
    title VARCHAR(512) NOT NULL,
    original_url VARCHAR(1024) NOT NULL,
    doc_type VARCHAR(64), -- Government Order (GO), Circular, Guidelines, Application Form, Notification, Amendment
    document_language VARCHAR(32) DEFAULT 'en', -- en, ml, bilingual
    publication_date DATE,
    download_date TIMESTAMPTZ,
    file_type VARCHAR(32), -- pdf, docx, html
    file_size_bytes BIGINT,
    sha256_hash VARCHAR(64) UNIQUE,
    current_version INT DEFAULT 1,
    file_path VARCHAR(512),
    processing_status VARCHAR(32) DEFAULT 'PENDING', -- PENDING, EXTRACTING, PROCESSED, FAILED
    verification_status VARCHAR(32) DEFAULT 'UNVERIFIED', -- UNVERIFIED, VERIFIED, REJECTED
    error_log TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. Document Versions (Change history & amendments)
CREATE TABLE IF NOT EXISTS document_versions (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(64) REFERENCES scheme_documents(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    sha256_hash VARCHAR(64) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    change_summary TEXT,
    detected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8. Extracted Document Content & Vector Embeddings (Chunk-level)
CREATE TABLE IF NOT EXISTS extracted_document_content (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(64) REFERENCES scheme_documents(id) ON DELETE CASCADE,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE SET NULL,
    page_number INT NOT NULL,
    chunk_index INT NOT NULL,
    content_text TEXT NOT NULL,
    content_malayalam TEXT,
    section_title VARCHAR(255),
    is_table BOOLEAN DEFAULT FALSE,
    table_data_json JSONB,
    embedding vector(1536), -- Vector embedding for RAG semantic search
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 9. Scheme Amendments
CREATE TABLE IF NOT EXISTS scheme_amendments (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE CASCADE,
    original_document_id VARCHAR(64) REFERENCES scheme_documents(id) ON DELETE SET NULL,
    amending_document_id VARCHAR(64) REFERENCES scheme_documents(id) ON DELETE SET NULL,
    amendment_type VARCHAR(64), -- EXTENSION, SUBSIDY_REVISION, ELIGIBILITY_MODIFICATION, CANCELLATION, SUPERSEDED
    order_number VARCHAR(128),
    order_date DATE,
    description TEXT,
    requires_admin_review BOOLEAN DEFAULT TRUE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 10. Scheme Districts (Applicable Kerala Districts)
CREATE TABLE IF NOT EXISTS scheme_districts (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE CASCADE,
    district_name VARCHAR(64) NOT NULL,
    panchayat_or_block VARCHAR(128),
    is_statewide BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 11. Scheme Crops (Target Agricultural Crops)
CREATE TABLE IF NOT EXISTS scheme_crops (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE CASCADE,
    crop_name VARCHAR(128) NOT NULL,
    crop_category VARCHAR(64), -- Cereals, Spices, Plantation, Horticulture, Tuber, Floriculture, Fodder
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 12. Application Guidelines & Required Documents Checklist
CREATE TABLE IF NOT EXISTS application_guidelines (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE CASCADE,
    document_name VARCHAR(255) NOT NULL, -- Aadhaar, Land Tax Receipt, Possession Certificate, Bank Passbook
    is_mandatory BOOLEAN DEFAULT TRUE,
    issuing_authority VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 13. Farmer Profiles (For Eligibility Matching)
CREATE TABLE IF NOT EXISTS farmer_profiles (
    id VARCHAR(64) PRIMARY KEY,
    full_name VARCHAR(255),
    district VARCHAR(64) NOT NULL,
    taluk VARCHAR(64),
    panchayat VARCHAR(128),
    farmer_type VARCHAR(64), -- Marginal (<1 ha), Small (1-2 ha), Semi-Medium, Medium, Large, Tenant
    total_land_acres NUMERIC(8, 2),
    primary_crops TEXT[],
    irrigation_type VARCHAR(64), -- Rainfed, Well, River/Canal, Drip/Sprinkler
    annual_income NUMERIC(12, 2),
    caste_category VARCHAR(64), -- General, OBC, SC, ST
    has_kisan_credit_card BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 14. Verification History (Audit log of all manual and automated reviews)
CREATE TABLE IF NOT EXISTS verification_history (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(64) REFERENCES schemes(id) ON DELETE CASCADE,
    verified_by VARCHAR(64) NOT NULL, -- Automated-AI, Admin-Manual
    action VARCHAR(64) NOT NULL, -- APPROVED, REJECTED, MODIFIED, EXTENSION_CONFIRMED, MARKED_INACTIVE
    previous_status VARCHAR(32),
    new_status VARCHAR(32),
    reason TEXT,
    verified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 15. Crawler Logs (Audit trail of every crawl cycle)
CREATE TABLE IF NOT EXISTS crawler_logs (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(64) REFERENCES government_sources(id) ON DELETE SET NULL,
    crawl_session_id VARCHAR(64) NOT NULL,
    urls_visited INT DEFAULT 0,
    documents_discovered INT DEFAULT 0,
    documents_downloaded INT DEFAULT 0,
    new_schemes_found INT DEFAULT 0,
    duration_seconds NUMERIC(8, 2),
    status VARCHAR(32), -- SUCCESS, PARTIAL_SUCCESS, FAILED
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ
);

-- Create Performance & Search Indexes
CREATE INDEX IF NOT EXISTS idx_schemes_status ON schemes(status);
CREATE INDEX IF NOT EXISTS idx_schemes_classification ON schemes(classification);
CREATE INDEX IF NOT EXISTS idx_schemes_dept ON schemes(department_id);
CREATE INDEX IF NOT EXISTS idx_scheme_districts_dist ON scheme_districts(district_name);
CREATE INDEX IF NOT EXISTS idx_scheme_crops_crop ON scheme_crops(crop_name);
CREATE INDEX IF NOT EXISTS idx_docs_hash ON scheme_documents(sha256_hash);
CREATE INDEX IF NOT EXISTS idx_content_doc ON extracted_document_content(document_id);
"""

import socket
import time

def get_connection(retries: int = 4, backoff: float = 1.5):
    """Returns a new psycopg connection with dictionary row factory and retry resilience."""
    last_err = None
    for attempt in range(retries):
        try:
            return psycopg.connect(DATABASE_URL, row_factory=dict_row)
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff * (1.5 ** attempt))
    raise last_err

def init_db():
    """Initializes the database schema and creates all tables."""
    logger.info("Initializing KrishiMitra database schema...")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.commit()
        logger.info("KrishiMitra database tables initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e
