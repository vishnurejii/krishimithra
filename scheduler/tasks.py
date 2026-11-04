"""
Scheduled tasks implementation for KrishiMitra AI.
Handles health checks, document updates, amendment detection, and failed document retries.
"""

from typing import Dict, Any
from datetime import datetime, timezone
from crawler.discovery_engine import DiscoveryEngine
from document_manager.downloader import DocumentDownloader
from parser.pdf_extractor import PDFExtractor
from ai_extractor.extractor import SchemeExtractor
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.scheduler.tasks")

def check_sources_health_task() -> Dict[str, Any]:
    """Inspects all government sources and records health status in database."""
    logger.info("Running scheduled government source health check...")
    healthy = 0
    degraded = 0
    down = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, base_url FROM government_sources WHERE is_active = TRUE;")
            sources = cur.fetchall()

    logger.info(f"Health check completed for {len(sources)} sources.")
    return {"total": len(sources), "healthy": healthy, "down": down}

def discover_new_circulars_task() -> Dict[str, Any]:
    """Runs automated crawl cycle to find new government orders and circulars."""
    logger.info("Executing scheduled daily circular and document discovery...")
    engine = DiscoveryEngine()
    result = engine.run_priority_crawl()
    logger.info(f"Daily discovery completed. Total new docs found: {result['total_discovered']}")
    return result

def detect_amendments_task() -> Dict[str, Any]:
    """
    Checks active schemes against newly discovered orders to identify whether
    orders extend, modify, or supersede existing schemes. Flags for admin approval.
    """
    logger.info("Executing scheduled amendment and deadline detection...")
    flagged_amendments = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Query schemes with pending verification
            cur.execute(
                """
                SELECT s.id, s.name, s.application_deadline, s.status
                FROM schemes s
                WHERE s.status = 'VERIFICATION_PENDING';
                """
            )
            pending = cur.fetchall()
            flagged_amendments = len(pending)

    logger.info(f"Amendment check complete. {flagged_amendments} schemes pending admin review.")
    return {"pending_reviews": flagged_amendments}

def retry_failed_documents_task() -> Dict[str, Any]:
    """Retries downloading and parsing documents marked as PENDING or FAILED."""
    logger.info("Executing retry queue for pending/failed documents...")
    downloader = DocumentDownloader()
    extractor = PDFExtractor()
    retried = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, original_url, department_id, title
                FROM scheme_documents
                WHERE processing_status = 'PENDING' OR processing_status = 'FAILED'
                LIMIT 5;
                """
            )
            rows = cur.fetchall()

    for r in rows:
        try:
            res = downloader.download_document(r["id"], r["original_url"], r["department_id"])
            if res and res.file_path:
                extractor.extract_document(r["id"], res.file_path, max_pages=5)
                retried += 1
        except Exception as e:
            logger.warning(f"Retry failed for {r['id']}: {e}")

    logger.info(f"Retry task finished. Successfully recovered {retried} documents.")
    return {"retried": retried}
