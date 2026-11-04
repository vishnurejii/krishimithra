"""
Discovery Engine for KrishiMitra AI.
Orchestrates crawler runs across official sources, handles deduplication,
logs execution metrics in PostgreSQL, and registers newly discovered documents.
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import hashlib
from registry.source_registry import SourceRegistry
from registry.models import InvestigationStatus
from crawler.base_crawler import DiscoveredDocument
from crawler.adapters.kerala_agri_adapter import KeralaAgriCrawlerAdapter
from crawler.adapters.aims_adapter import AIMSKeralaAdapter
from crawler.adapters.animal_husbandry_adapter import AnimalHusbandryCrawlerAdapter
from crawler.adapters.commodity_boards_adapter import CommodityBoardsCrawlerAdapter
from crawler.adapters.central_schemes_adapter import CentralSchemesCrawlerAdapter
from crawler.general_crawler import GeneralDepartmentCrawler
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.discovery")

class DiscoveryEngine:
    def __init__(self, registry: Optional[SourceRegistry] = None):
        from document_manager.downloader import DocumentDownloader
        self.registry = registry or SourceRegistry()
        self.downloader = DocumentDownloader()

    def run_department_crawl(self, dept_id: str, auto_download: bool = True) -> List[DiscoveredDocument]:
        """Runs the appropriate crawler adapter for a given department ID."""
        dept = self.registry.get_department(dept_id)
        if not dept:
            raise ValueError(f"Unknown department ID: {dept_id}")

        logger.info(f"Initiating crawl cycle for department: {dept.name} ({dept.id})")
        session_id = f"crawl_{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        # Update department status in database
        self._update_department_status(dept_id, InvestigationStatus.INVESTIGATING)

        crawler = None
        if dept_id == "KL_AGRI_DEPT":
            crawler = KeralaAgriCrawlerAdapter(dept_id, f"SRC_{dept_id}", dept.official_website)
        elif dept_id == "KL_AIMS_PORTAL":
            crawler = AIMSKeralaAdapter(dept_id, f"SRC_{dept_id}", dept.official_website)
        elif dept_id == "KL_AHD_DEPT":
            crawler = AnimalHusbandryCrawlerAdapter(dept_id, f"SRC_{dept_id}", dept.official_website)
        elif dept_id in ["BD_COCONUT", "BD_RUBBER", "BD_SPICES", "BD_COFFEE", "BD_NABARD"]:
            crawler = CommodityBoardsCrawlerAdapter(target_dept_id=dept_id)
        elif dept_id in ["CEN_PM_KISAN", "CEN_PMFBY", "CEN_MIDH", "CEN_AIF", "CEN_SOIL_HEALTH", "CEN_PM_KUSUM", "CEN_RKVY", "CEN_MISS_KCC"]:
            crawler = CentralSchemesCrawlerAdapter(target_dept_id=dept_id)
        else:
            entry_points = [dept.official_website]
            if getattr(dept, "scheme_listing_url", None) and dept.scheme_listing_url != dept.official_website:
                entry_points.append(dept.scheme_listing_url)
            crawler = GeneralDepartmentCrawler(dept_id, f"SRC_{dept_id}", dept.official_website, entry_points=entry_points, max_depth=1, max_pages=8)

        discovered = []
        downloaded_count = 0
        status = "SUCCESS"
        error_msg = None

        try:
            discovered = crawler.crawl()
            # Save discovered documents in database
            self._save_discovered_documents(discovered)

            # Automatically download discovered documents to storage
            if auto_download and discovered:
                logger.info(f"Downloading {len(discovered)} discovered documents for {dept_id}...")
                for doc in discovered:
                    doc_id = f"doc_{hashlib.md5(doc.original_url.encode()).hexdigest()[:12]}"
                    dl_res = self.downloader.download_document(doc_id, doc.original_url, doc.department_id)
                    if dl_res and (dl_res.file_path or dl_res.is_duplicate):
                        downloaded_count += 1

            new_status = InvestigationStatus.DOCUMENTS_COLLECTED if discovered else InvestigationStatus.INVESTIGATING
            self._update_department_status(dept_id, new_status)
        except Exception as e:
            status = "FAILED"
            error_msg = str(e)
            logger.error(f"Error during crawl of {dept_id}: {e}")

        duration = round(time.time() - start_time, 2)
        urls_visited = len(crawler.visited_urls) if crawler else 0

        # Log crawl execution
        self._log_crawl_session(
            source_id=f"SRC_{dept_id}",
            session_id=session_id,
            urls_visited=urls_visited,
            documents_discovered=len(discovered),
            documents_downloaded=downloaded_count,
            duration_seconds=duration,
            status=status,
            error_message=error_msg
        )

        logger.info(f"Crawl session {session_id} finished for {dept_id} in {duration}s. Discovered: {len(discovered)}, Downloaded: {downloaded_count}")
        return discovered

    def run_priority_crawl(self) -> Dict[str, Any]:
        """Runs crawler for core and high-priority agriculture departments."""
        priority_depts = [
            "KL_AGRI_DEPT",
            "KL_AIMS_PORTAL",
            "KL_AHD_DEPT",
            "KL_DAIRY_DEPT",
            "KL_FISHERIES_DEPT",
            "BD_COCONUT",
            "CEN_PM_KISAN"
        ]

        logger.info(f"Running Priority Crawl across {len(priority_depts)} departments...")
        total_discovered = 0
        total_downloaded = 0
        results = {}

        for dept_id in priority_depts:
            try:
                docs = self.run_department_crawl(dept_id, auto_download=True)
                results[dept_id] = len(docs)
                total_discovered += len(docs)
            except Exception as e:
                logger.error(f"Failed priority crawl for {dept_id}: {e}")
                results[dept_id] = 0

        logger.info(f"Priority crawl finished. Total documents discovered: {total_discovered}")
        return {
            "total_discovered": total_discovered,
            "department_breakdown": results
        }

    def _save_discovered_documents(self, documents: List[DiscoveredDocument]):
        """Persists discovered documents into scheme_documents table."""
        if not documents:
            return

        with get_connection() as conn:
            with conn.cursor() as cur:
                for doc in documents:
                    doc_id = f"doc_{hashlib.md5(doc.original_url.encode()).hexdigest()[:12]}"
                    cur.execute(
                        """
                        INSERT INTO scheme_documents (
                            id, department_id, title, original_url, doc_type,
                            document_language, file_type, processing_status, verification_status,
                            updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING', 'UNVERIFIED', CURRENT_TIMESTAMP)
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            department_id = EXCLUDED.department_id,
                            updated_at = CURRENT_TIMESTAMP;
                        """,
                        (
                            doc_id, doc.department_id, doc.title, doc.original_url,
                            doc.doc_type, doc.language, doc.file_type
                        )
                    )
            conn.commit()

    def _update_department_status(self, dept_id: str, status: InvestigationStatus):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE government_departments
                    SET investigation_status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (status.value, dept_id)
                )
            conn.commit()

    def _log_crawl_session(self, source_id: str, session_id: str, urls_visited: int, documents_discovered: int, documents_downloaded: int, duration_seconds: float, status: str, error_message: Optional[str] = None):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO crawler_logs (
                            source_id, crawl_session_id, urls_visited, documents_discovered,
                            documents_downloaded, duration_seconds, status, error_message, ended_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                        """,
                        (
                            source_id, session_id, urls_visited, documents_discovered,
                            documents_downloaded, duration_seconds, status, error_message
                        )
                    )
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not log crawl session: {e}")
