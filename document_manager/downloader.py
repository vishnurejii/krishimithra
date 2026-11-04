"""
Automatic Document Downloader and Deduplication Engine for KrishiMitra AI.
Downloads discovered PDFs, computes SHA-256 hash, detects exact duplicates,
handles changed/superseded versions, and updates PostgreSQL records.
"""

import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from crawler.session import GovernmentSession
from document_manager.models import DocumentDownloadResult
from document_manager.storage import DocumentStorage
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.document_manager.downloader")

class DocumentDownloader:
    def __init__(self, storage: Optional[DocumentStorage] = None):
        self.session = GovernmentSession()
        self.storage = storage or DocumentStorage()

    def download_document(self, doc_id: str, original_url: str, department_id: str) -> Optional[DocumentDownloadResult]:
        """
        Downloads a document from its official government URL,
        hashes content with SHA-256, verifies duplication, and handles versioning.
        Uses streamed chunks to prevent memory spikes on large PDFs.
        """
        # Check if already downloaded and exists on disk
        existing = self._get_existing_document(doc_id)
        if existing and existing.get("file_path") and Path(existing.get("file_path")).exists() and existing.get("sha256_hash"):
            logger.info(f"Document {doc_id} already exists locally at {existing['file_path']}. Skipping re-download.")
            return DocumentDownloadResult(
                document_id=doc_id,
                original_url=original_url,
                file_path=existing["file_path"],
                sha256_hash=existing["sha256_hash"],
                file_size_bytes=Path(existing["file_path"]).stat().st_size,
                is_duplicate=True,
                new_version=existing.get("current_version") or 1
            )

        logger.info(f"Downloading document: {doc_id} from {original_url}")
        try:
            resp = self.session.get(original_url, timeout=30, check_robots=False, stream=True)
            if resp.status_code != 200:
                logger.warning(f"Download failed for {original_url}: HTTP {resp.status_code}")
                self._record_error(doc_id, f"HTTP {resp.status_code}")
                return None

            ext = original_url.split(".")[-1].split("?")[0].lower()
            if ext not in ["pdf", "docx", "doc", "xlsx", "xls", "zip"]:
                ext = "pdf"

            current_version = (existing.get("current_version") or 1) if existing else 1
            save_path = self.storage.get_destination_path(department_id, doc_id, current_version, ext)
            temp_path = save_path.with_suffix(".part")

            hasher = hashlib.sha256()
            file_size = 0
            with open(temp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        hasher.update(chunk)
                        file_size += len(chunk)

            if file_size == 0:
                if temp_path.exists():
                    temp_path.unlink()
                self._record_error(doc_id, "Empty response body")
                return None

            sha256 = hasher.hexdigest()

            is_dup = False
            is_updated = False
            new_version = current_version

            if existing:
                current_hash = existing.get("sha256_hash")
                if current_hash == sha256 and existing.get("file_path") and Path(existing.get("file_path")).exists():
                    logger.info(f"Duplicate content detected for {doc_id} (hash={sha256[:8]}). Skipping save.")
                    if temp_path.exists():
                        temp_path.unlink()
                    return DocumentDownloadResult(
                        document_id=doc_id,
                        original_url=original_url,
                        file_path=existing.get("file_path", ""),
                        sha256_hash=sha256,
                        file_size_bytes=file_size,
                        is_duplicate=True,
                        new_version=current_version
                    )
                elif current_hash and current_hash != sha256:
                    is_updated = True
                    new_version = current_version + 1
                    save_path = self.storage.get_destination_path(department_id, doc_id, new_version, ext)
                    logger.info(f"Document content changed for {doc_id}! Incrementing to v{new_version}")

            # Rename temp part file to final destination
            if temp_path.exists():
                temp_path.replace(save_path)

            # Update PostgreSQL database
            self._save_to_database(doc_id, str(save_path), sha256, file_size, new_version, is_updated)

            logger.info(f"Successfully saved {doc_id} to {save_path} ({file_size} bytes)")
            return DocumentDownloadResult(
                document_id=doc_id,
                original_url=original_url,
                file_path=str(save_path),
                sha256_hash=sha256,
                file_size_bytes=file_size,
                is_duplicate=False,
                is_updated_version=is_updated,
                new_version=new_version
            )

        except Exception as e:
            logger.error(f"Exception downloading {original_url}: {e}")
            self._record_error(doc_id, str(e))
            return None

    def _get_existing_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT sha256_hash, current_version, file_path FROM scheme_documents WHERE id = %s;",
                    (doc_id,)
                )
                return cur.fetchone()

    def _save_to_database(self, doc_id: str, file_path: str, sha256: str, file_size: int, version: int, is_updated: bool):
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if this exact file hash already exists under another document ID
                cur.execute("SELECT id, file_path FROM scheme_documents WHERE sha256_hash = %s AND id != %s;", (sha256, doc_id))
                other = cur.fetchone()
                if other:
                    cur.execute(
                        """
                        UPDATE scheme_documents
                        SET file_path = %s,
                            file_size_bytes = %s,
                            current_version = %s,
                            download_date = CURRENT_TIMESTAMP,
                            processing_status = 'DUPLICATE',
                            error_log = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                        """,
                        (other["file_path"], file_size, version, f"Duplicate of {other['id']}", doc_id)
                    )
                    conn.commit()
                    return

                cur.execute(
                    """
                    UPDATE scheme_documents
                    SET file_path = %s,
                        sha256_hash = %s,
                        file_size_bytes = %s,
                        current_version = %s,
                        download_date = CURRENT_TIMESTAMP,
                        processing_status = 'DOWNLOADED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (file_path, sha256, file_size, version, doc_id)
                )

                # If updated version, insert history into document_versions
                if is_updated:
                    cur.execute(
                        """
                        INSERT INTO document_versions (document_id, version_number, sha256_hash, file_path, change_summary)
                        VALUES (%s, %s, %s, %s, 'Government order content modified on source portal');
                        """,
                        (doc_id, version, sha256, file_path)
                    )
            conn.commit()

    def _record_error(self, doc_id: str, error_msg: str):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE scheme_documents
                        SET processing_status = 'FAILED',
                            error_log = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                        """,
                        (error_msg, doc_id)
                    )
                conn.commit()
        except Exception:
            pass
