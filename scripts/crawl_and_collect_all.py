"""
KrishiMitra AI - Comprehensive Multi-Portal Crawler and Document Collector
Crawls all Kerala Agriculture and Farmer Impacting Departments, Statutory Boards,
and Central Ministries, and collects (downloads) all PDFs, circulars, and guidelines.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure proper encoding and workspace path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection
from core.logger import get_logger
from registry.departments_data import DEPARTMENTS_REGISTRY
from crawler.discovery_engine import DiscoveryEngine
from document_manager.downloader import DocumentDownloader

logger = get_logger("krishimitra.crawler.full_collector")

def download_pending_documents(downloader: DocumentDownloader) -> Dict[str, int]:
    """Download any previously discovered documents that are still pending or failed."""
    print("\n" + "=" * 80)
    print("PHASE 1: DOWNLOADING ALL EXISTING PENDING/UNDOWNLOADED REGISTERED DOCUMENTS")
    print("=" * 80)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, department_id, original_url, title
                FROM scheme_documents
                WHERE file_path IS NULL
                ORDER BY department_id;
            """)
            pending = cur.fetchall()

    print(f"Found {len(pending)} pending documents in database awaiting download.")
    success_count = 0
    fail_count = 0

    for i, doc in enumerate(pending, 1):
        doc_id = doc["id"]
        url = doc["original_url"]
        dept = doc["department_id"]
        title = (doc["title"] or "Document")[:50]

        print(f"[{i}/{len(pending)}] [{dept}] Downloading: {title} ...")
        try:
            res = downloader.download_document(doc_id, url, dept)
            if res and (res.file_path or res.is_duplicate):
                mb = round((res.file_size_bytes or 0) / (1024 * 1024), 2)
                print(f"      -> SUCCESS: {res.file_path} ({mb} MB)")
                success_count += 1
            else:
                print(f"      -> FAILED or HTTP error for {url}")
                fail_count += 1
        except Exception as e:
            print(f"      -> EXCEPTION: {e}")
            fail_count += 1

    print(f"\nPhase 1 Complete. Recovered/Downloaded: {success_count}, Failed/Dead Links: {fail_count}")
    return {"recovered": success_count, "failed": fail_count}

def crawl_and_collect_all_departments(engine: DiscoveryEngine) -> Dict[str, Any]:
    """Crawl and collect documents across all 47 agriculture & farmer impacting departments."""
    print("\n" + "=" * 80)
    print("PHASE 2: CRAWLING SITES & COLLECTING NEW DOCUMENTS ACROSS ALL AGRICULTURE PORTALS")
    print("=" * 80)

    # Get all agriculture and farmer impacting departments
    agri_depts = [d for d in DEPARTMENTS_REGISTRY if d.get("has_agriculture_schemes")]
    print(f"Targeting {len(agri_depts)} Agriculture & Allied Departments / Boards / Portals.")

    # High-priority core agriculture departments, commodity boards, and central schemes
    priority_order = [
        # Core state agriculture
        "KL_AGRI_DEPT",
        "KL_AIMS_PORTAL",
        "KL_KATHIR_PORTAL",
        "KL_AHD_DEPT",
        "KL_DAIRY_DEPT",
        "KL_FISHERIES_DEPT",
        "KL_SOIL_CONS_DEPT",
        "KL_COOPERATION_DEPT",
        "KL_KSCARDB",
        "KL_KUDUMBASHREE",
        "KL_KAU_ACAD",
        "KL_VFPCK",
        "KL_HORTICORP",
        # Commodity boards
        "BD_COCONUT",
        "BD_RUBBER",
        "BD_SPICES",
        "BD_COFFEE",
        "BD_NABARD",
        # Central agricultural schemes
        "CEN_PM_KISAN",
        "CEN_PMFBY",
        "CEN_MIDH",
        "CEN_AIF",
        "CEN_SOIL_HEALTH",
        "CEN_PM_KUSUM",
        "CEN_RKVY",
        "CEN_MISS_KCC",
    ]

    # Reorder agri_depts based on priority_order
    ordered_depts = []
    dept_map = {d["id"]: d for d in agri_depts}
    for p_id in priority_order:
        if p_id in dept_map:
            ordered_depts.append(dept_map[p_id])
    for d in agri_depts:
        if d not in ordered_depts:
            ordered_depts.append(d)

    crawl_results = {}
    total_new_docs = 0

    for i, dept in enumerate(ordered_depts, 1):
        dept_id = dept["id"]
        name = dept["name"]
        url = dept["official_website"]
        print(f"\n[{i}/{len(ordered_depts)}] CRAWLING: {name} ({dept_id})")
        print(f"      Official URL: {url}")

        try:
            discovered = engine.run_department_crawl(dept_id, auto_download=True)
            doc_count = len(discovered)
            crawl_results[dept_id] = doc_count
            total_new_docs += doc_count
            print(f"      -> COMPLETED: {doc_count} documents discovered & processed.")
        except Exception as e:
            print(f"      -> ERROR: {e}")
            crawl_results[dept_id] = 0

    return {
        "total_discovered": total_new_docs,
        "department_breakdown": crawl_results
    }

def print_final_summary():
    """Print the final document collection status from Neon PostgreSQL."""
    print("\n" + "=" * 80)
    print("FINAL HARVEST & COLLECTION REPORT (NEON POSTGRESQL)")
    print("=" * 80)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.name as dept_name, sd.department_id,
                       COUNT(*) as total_documents,
                       COUNT(CASE WHEN sd.file_path IS NOT NULL THEN 1 END) as downloaded_files,
                       SUM(COALESCE(sd.file_size_bytes, 0)) as total_bytes
                FROM scheme_documents sd
                LEFT JOIN government_departments d ON sd.department_id = d.id
                GROUP BY d.name, sd.department_id
                ORDER BY total_documents DESC;
            """)
            rows = cur.fetchall()
            grand_total_docs = 0
            grand_total_downloaded = 0
            grand_total_bytes = 0

            for r in rows:
                dept_name = (r["dept_name"] or r["department_id"])[:45]
                docs = r["total_documents"]
                dl = r["downloaded_files"]
                mb = round(r["total_bytes"] / (1024 * 1024), 2)
                grand_total_docs += docs
                grand_total_downloaded += dl
                grand_total_bytes += (r["total_bytes"] or 0)
                print(f"  - {dept_name:<46} | Dept: {r['department_id']:<20} | Discovered: {docs:<4} | Saved: {dl:<4} ({mb} MB)")

            print("-" * 80)
            total_mb = round(grand_total_bytes / (1024 * 1024), 2)
            print(f"  GRAND TOTAL REGISTERED DOCUMENTS ACROSS ALL SITES: {grand_total_docs}")
            print(f"  GRAND TOTAL COLLECTED ON DISK:                     {grand_total_downloaded} ({total_mb} MB)")
            print("=" * 80)

def main():
    start_time = time.time()
    downloader = DocumentDownloader()
    engine = DiscoveryEngine()

    # 1. Download pending documents that were already discovered
    download_pending_documents(downloader)

    # 2. Run crawl and collect across all 47 agriculture portals
    crawl_and_collect_all_departments(engine)

    # 3. Print final report
    print_final_summary()

    # 4. Update COVERAGE_REPORT.md
    try:
        from registry.source_registry import SourceRegistry
        from registry.coverage_matrix import SchemeCoverageMatrix
        matrix_engine = SchemeCoverageMatrix(SourceRegistry())
        md_content = matrix_engine.generate_markdown_report()
        report_path = BASE_DIR / "COVERAGE_REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"\nUpdated Coverage Matrix saved to: {report_path}")
    except Exception as e:
        print(f"Note: Could not regenerate markdown coverage matrix: {e}")

    elapsed = round(time.time() - start_time, 1)
    print(f"\nAll operations completed successfully in {elapsed} seconds.")

if __name__ == "__main__":
    main()
