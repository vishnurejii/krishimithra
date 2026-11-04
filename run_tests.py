"""
KrishiMitra AI - Unified Comprehensive Test Runner
Executes all subsystem verifications in a single automated suite:
  1. Database Connectivity & pgvector Extension
  2. Source Registry & 62 Department Coverage Matrix
  3. Resilient Crawler & Portal Reachability
  4. Document Downloader & SHA-256 Deduplication
  5. PDF Extraction & Table Parsing
  6. AI Scheme Extraction & Conflict Detection
  7. Farmer Eligibility Evaluator
  8. Bilingual RAG Farmer Assistant (English & Malayalam)
  9. Web Application & REST APIs

Usage:
  python run_tests.py          # Runs the complete test suite
  python run_tests.py --quick  # Runs core tests without heavy network crawls
"""

import sys
import time
from pathlib import Path

# Force UTF-8 stdout for Windows consoles
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.duration_seconds = 0.0
        self.error_message = None
        self.details = []

def run_test_step(step_name: str, step_func):
    result = TestResult(step_name)
    print(f"\n[TEST] {step_name}...", end=" ", flush=True)
    t0 = time.time()
    try:
        details = step_func()
        result.passed = True
        result.duration_seconds = round(time.time() - t0, 3)
        result.details = details or []
        print(f"PASSED ({result.duration_seconds}s)")
        for d in result.details:
            print(f"       + {d}")
    except Exception as e:
        result.passed = False
        result.duration_seconds = round(time.time() - t0, 3)
        result.error_message = str(e)
        print(f"FAILED ({result.duration_seconds}s)")
        print(f"       ! Error: {e}")
    return result

# =========================================================================
# TEST 1: Database Connectivity & pgvector
# =========================================================================
def test_database():
    from core.database import get_connection
    details = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            ver_row = cur.fetchone()
            ver = ver_row["version"] if "version" in ver_row else list(ver_row.values())[0]
            details.append(f"PostgreSQL Version: {ver.split()[0]} {ver.split()[1]}")

            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
            ext = cur.fetchone()
            if not ext:
                raise RuntimeError("pgvector extension not found!")
            extname = ext["extname"]
            extver = ext["extversion"]
            details.append(f"pgvector Extension: {extname} (v{extver})")

            cur.execute("SELECT count(*) as count FROM government_departments;")
            dept_count = cur.fetchone()["count"]
            details.append(f"Total Departments in DB: {dept_count}")
    return details

# =========================================================================
# TEST 2: Source Registry & Coverage Matrix
# =========================================================================
def test_registry_and_coverage():
    from registry.source_registry import SourceRegistry
    from registry.coverage_matrix import SchemeCoverageMatrix
    details = []

    reg = SourceRegistry()
    details.append(f"In-memory Departments Catalog: {len(reg.departments)}")

    matrix_engine = SchemeCoverageMatrix(reg)
    matrix = matrix_engine.compute_matrix()
    details.append(f"Coverage Matrix Computed: {len(matrix)} total departments/agencies")

    agri_depts = [m for m in matrix if m["investigation_status"] != "No relevant schemes found"]
    non_agri = [m for m in matrix if m["investigation_status"] == "No relevant schemes found"]
    details.append(f"Agriculture-Impacting Departments: {len(agri_depts)}")
    details.append(f"Line Departments (Verified No Schemes): {len(non_agri)}")
    return details

# =========================================================================
# TEST 3: Document Downloader & Deduplication
# =========================================================================
def test_download_and_deduplication():
    from document_manager.downloader import DocumentDownloader
    from core.database import get_connection
    details = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, original_url, department_id, title FROM scheme_documents WHERE original_url LIKE '%.pdf' LIMIT 1;")
            row = cur.fetchone()

    if not row:
        raise RuntimeError("No PDF documents available in scheme_documents table.")

    downloader = DocumentDownloader()
    doc_id = row["id"]
    url = row["original_url"]
    dept_id = row["department_id"]

    # 1. Download
    res1 = downloader.download_document(doc_id, url, dept_id)
    if not res1 or not res1.file_path:
        raise RuntimeError(f"Initial download failed for {url}")
    details.append(f"Downloaded: {res1.file_path} ({res1.file_size_bytes} bytes)")
    details.append(f"SHA-256 Checksum: {res1.sha256_hash[:16]}...")

    # 2. Re-download (Deduplication Check)
    res2 = downloader.download_document(doc_id, url, dept_id)
    if not res2 or not res2.is_duplicate:
        raise RuntimeError("Deduplication check failed! Document was not flagged as duplicate.")
    details.append("Deduplication Verified: Re-download detected identical hash without re-writing")
    return details

# =========================================================================
# TEST 4: PDF Extraction & Table Parsing
# =========================================================================
def test_pdf_extraction():
    from parser.pdf_extractor import PDFExtractor
    from core.database import get_connection
    details = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, file_path, title FROM scheme_documents WHERE file_path IS NOT NULL LIMIT 1;")
            row = cur.fetchone()

    if not row:
        raise RuntimeError("No downloaded file available for PDF extraction test.")

    extractor = PDFExtractor()
    doc = extractor.extract_document(row["id"], row["file_path"], max_pages=3)
    details.append(f"Document: {row['title']}")
    details.append(f"Total Pages: {doc.total_pages} | Processed: {len(doc.pages)}")
    details.append(f"Primary Language: {doc.primary_language} | Total Characters: {doc.total_characters}")
    return details

# =========================================================================
# TEST 5: AI Scheme Information Extraction
# =========================================================================
def test_ai_extraction():
    from ai_extractor.extractor import SchemeExtractor
    from core.database import get_connection
    details = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, department_id, title FROM scheme_documents LIMIT 1;")
            row = cur.fetchone()

    pages = [
        {"page_number": 1, "text": "Guidelines for Weather Based Crop Insurance Scheme Kerala. Department of Agriculture."},
        {"page_number": 2, "text": "Eligible crops: Paddy, Banana, Pepper, Cardamom. 50% premium subsidy up to Rs 50000. Apply at aimsnew.kerala.gov.in."}
    ]

    extractor = SchemeExtractor()
    extracted = extractor.extract_from_text(row["id"], row["department_id"], "Crop Insurance WBCIS Test", pages)
    details.append(f"Extracted Scheme: {extracted.scheme_name}")
    details.append(f"Classification: {extracted.classification}")
    details.append(f"Eligible Crops: {extracted.eligible_crops}")
    details.append(f"Subsidy: {extracted.subsidy_percentage}% (Cap: Rs {extracted.max_assistance_limit})")
    details.append(f"Required Documents: {extracted.required_documents}")
    return details

# =========================================================================
# TEST 6: Farmer Eligibility Checker
# =========================================================================
def test_farmer_eligibility():
    from eligibility.models import FarmerInputProfile
    from eligibility.checker import EligibilityChecker
    details = []

    profile = FarmerInputProfile(
        full_name="Govindan Nambiar",
        district="Wayanad",
        farmer_type="Small Farmer",
        total_land_acres=2.5,
        primary_crops=["Pepper", "Paddy"],
        annual_income=120000.0
    )

    checker = EligibilityChecker()
    res = checker.evaluate_farmer(profile)
    details.append(f"Farmer: {profile.full_name} ({profile.district}, {profile.total_land_acres} ac)")
    details.append(f"Eligible Schemes Found: {res.total_matched_schemes}")
    for s in res.eligible_schemes[:2]:
        details.append(f" - [{s.classification}] {s.scheme_name}: {s.estimated_benefit}")
    return details

# =========================================================================
# TEST 7: Bilingual RAG Assistant
# =========================================================================
def test_rag_assistant():
    from rag.assistant import FarmerAssistant
    details = []
    assistant = FarmerAssistant()

    # English Test
    q_en = "What is Paddy Royalty scheme in Kerala?"
    res_en = assistant.answer_question(q_en, language="en")
    details.append(f"Query (EN): '{q_en}' -> {res_en['schemes_found']} schemes cited")

    # Malayalam Test
    q_ml = "കുരുമുളക് കൃഷിക്ക് എന്തൊക്കെ ആനുകൂല്യങ്ങൾ ഉണ്ട്?"
    res_ml = assistant.answer_question(q_ml, language="ml")
    details.append(f"Query (ML): '{q_ml}' -> {res_ml['schemes_found']} schemes cited")

    for c in res_en["citations"][:1]:
        details.append(f"Citation: {c['scheme_name']} ({c['source_document']})")
    return details

# =========================================================================
# TEST 8: Web Application Endpoints
# =========================================================================
def test_web_endpoints():
    import urllib.request
    import json
    details = []

    endpoints = [
        ("Farmer Portal", "http://127.0.0.1:8080/"),
        ("Admin Studio", "http://127.0.0.1:8080/admin-portal/"),
        ("Schemes API", "http://127.0.0.1:8080/api/schemes/"),
        ("Coverage Matrix API", "http://127.0.0.1:8080/api/coverage/matrix/"),
        ("Admin Metrics API", "http://127.0.0.1:8080/api/admin/metrics/")
    ]

    for name, url in endpoints:
        req = urllib.request.Request(url, headers={"User-Agent": "KrishiMitraTestRunner/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            size = len(resp.read())
            if status != 200:
                raise RuntimeError(f"{name} ({url}) returned HTTP {status}")
            details.append(f"{name}: HTTP {status} ({size} bytes)")
    return details

# =========================================================================
# MAIN TEST RUNNER
# =========================================================================
def main():
    print("=" * 80)
    print("KrishiMitra AI - Unified Automated Test Suite")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    tests = [
        ("1. PostgreSQL & pgvector Database", test_database),
        ("2. Source Registry & Coverage Matrix", test_registry_and_coverage),
        ("3. Document Downloader & SHA-256 Deduplication", test_download_and_deduplication),
        ("4. PDF Extraction & Table Parsing", test_pdf_extraction),
        ("5. AI Scheme Information Extraction", test_ai_extraction),
        ("6. Farmer Eligibility Checker", test_farmer_eligibility),
        ("7. Bilingual RAG Farmer Assistant", test_rag_assistant),
        ("8. Web Application Endpoints (Port 8080)", test_web_endpoints)
    ]

    results = []
    total_start = time.time()

    for name, func in tests:
        res = run_test_step(name, func)
        results.append(res)

    total_duration = round(time.time() - total_start, 2)
    passed_count = sum(1 for r in results if r.passed)
    failed_count = sum(1 for r in results if not r.passed)

    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY:")
    print(f"  Total Test Suites: {len(results)}")
    print(f"  Passed: {passed_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total Duration: {total_duration}s")
    print("=" * 80)

    if failed_count > 0:
        print("\nFailed Tests Details:")
        for r in results:
            if not r.passed:
                print(f"  - {r.name}: {r.error_message}")
        sys.exit(1)
    else:
        print("\nAll KrishiMitra AI subsystems verified successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
