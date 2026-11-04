"""
Test for Stage 3: Document Downloader and SHA-256 Deduplication
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from document_manager.downloader import DocumentDownloader
from core.database import get_connection

def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, original_url, department_id, title FROM scheme_documents WHERE original_url LIKE '%.pdf' LIMIT 1;")
            row = cur.fetchone()

    if not row:
        print("No documents found in database.")
        return

    print("Target Document:", row["title"])
    print("URL:", row["original_url"])

    downloader = DocumentDownloader()

    # 1. First Download
    print("\n--- 1. Performing Initial Download ---")
    res1 = downloader.download_document(row["id"], row["original_url"], row["department_id"])
    print("Download 1 success:", res1 is not None)
    if res1:
        print("File saved to:", res1.file_path)
        print("SHA-256:", res1.sha256_hash)
        print("File Size:", res1.file_size_bytes, "bytes")
        print("Is duplicate:", res1.is_duplicate)

    # 2. Re-download (Deduplication Verification)
    print("\n--- 2. Performing Re-download (Deduplication Check) ---")
    res2 = downloader.download_document(row["id"], row["original_url"], row["department_id"])
    print("Download 2 success:", res2 is not None)
    if res2:
        print("Is duplicate detected:", res2.is_duplicate)
        print("SHA-256 matches:", res2.sha256_hash == res1.sha256_hash)

if __name__ == "__main__":
    main()
