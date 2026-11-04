"""
Targeted Crawler Script for Coconut Development Board (Kochi).
Crawls official portals, discovers PDFs/application guidelines, downloads files,
and registers everything in PostgreSQL.
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection
from core.logger import get_logger
from crawler.discovery_engine import DiscoveryEngine

logger = get_logger("krishimitra.crawler.coconut_board")

def main():
    print("=" * 80)
    print("KRISHIMITRA AI - COCONUT DEVELOPMENT BOARD (KOCHI) CRAWLER")
    print("Department ID: BD_COCONUT")
    print("Source ID:     SRC_BD_COCONUT")
    print("Official URLs: https://coconutboard.gov.in/ (Schemes, TMOC, Application Forms, etc.)")
    print("=" * 80)

    start_time = time.time()
    engine = DiscoveryEngine()

    print("\n[Step 1/2] Initiating discovery and document collection...")
    discovered = engine.run_department_crawl("BD_COCONUT", auto_download=True)
    duration = round(time.time() - start_time, 2)

    print(f"\n[Step 2/2] Crawl Completed in {duration} seconds.")
    print(f"Total documents discovered in this session: {len(discovered)}")

    # Fetch summary stats from PostgreSQL
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_docs,
                    COUNT(file_path) as downloaded_docs,
                    COALESCE(SUM(file_size_bytes), 0) as total_bytes
                FROM scheme_documents
                WHERE department_id = 'BD_COCONUT';
            """)
            stats = cur.fetchone()

            cur.execute("""
                SELECT id, title, doc_type, document_language, file_size_bytes, original_url
                FROM scheme_documents
                WHERE department_id = 'BD_COCONUT'
                ORDER BY created_at DESC
                LIMIT 25;
            """)
            sample_docs = cur.fetchall()

            cur.execute("""
                SELECT investigation_status, updated_at
                FROM government_departments
                WHERE id = 'BD_COCONUT';
            """)
            dept_status = cur.fetchone()

    total_mb = round((stats['total_bytes'] or 0) / (1024 * 1024), 2)
    print("\n" + "=" * 80)
    print("DATABASE SUMMARY FOR COCONUT DEVELOPMENT BOARD (BD_COCONUT):")
    print("=" * 80)
    print(f"Investigation Status: {dept_status['investigation_status']}")
    print(f"Total Documents in DB: {stats['total_docs']}")
    print(f"Downloaded Locally:   {stats['downloaded_docs']}")
    print(f"Total Download Volume: {total_mb} MB")

    print("\nRecent Documents Discovered / Collected:")
    for i, d in enumerate(sample_docs, 1):
        size_kb = round((d['file_size_bytes'] or 0) / 1024, 1)
        lang = d['document_language'] or 'en'
        dtype = d['doc_type'] or 'Guidelines'
        print(f"[{i:02d}] [{lang.upper()}] [{dtype}] {d['title']}")
        print(f"     URL: {d['original_url']} ({size_kb} KB)")

if __name__ == "__main__":
    main()

