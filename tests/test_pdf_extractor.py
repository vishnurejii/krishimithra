"""
Test for Stage 4: PDF Extraction and Text Analysis
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser.pdf_extractor import PDFExtractor
from core.database import get_connection

def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, file_path, title FROM scheme_documents WHERE file_path IS NOT NULL LIMIT 1;")
            row = cur.fetchone()

    if not row:
        print("No downloaded document found in database.")
        return

    print("Extracting document:", row["title"])
    print("File path:", row["file_path"])

    extractor = PDFExtractor()
    # Extract first 5 pages for validation
    res = extractor.extract_document(row["id"], row["file_path"], max_pages=5)

    print("\n--- Extraction Results ---")
    print("Total Document Pages:", res.total_pages)
    print("Pages Processed:", len(res.pages))
    print("Detected Language:", res.primary_language)
    print("Total Characters Extracted:", res.total_characters)

    for p in res.pages[:3]:
        print(f"\n[Page {p.page_number}] (Lang: {p.language}, Chars: {p.char_count}, Tables: {len(p.tables)}):")
        snippet = p.text[:250].replace("\n", " ")
        print(f"Snippet: {snippet}...")

if __name__ == "__main__":
    main()
