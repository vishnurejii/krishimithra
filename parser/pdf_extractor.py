"""
High-Performance PDF Text and Table Extractor for KrishiMitra AI.
Uses PyMuPDF (fitz) with automatic OCR fallback for scanned pages.
Preserves page numbers, table structures, and bilingual content.
"""

from pathlib import Path
from typing import Optional, List
import io
import fitz # PyMuPDF
from PIL import Image
from parser.models import ExtractedDocument, ExtractedPage, ExtractedTable
from parser.ocr_engine import OCREngine
from parser.normalizer import normalize_malayalam_text, detect_language
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.parser.pdf_extractor")

class PDFExtractor:
    def __init__(self, ocr_engine: Optional[OCREngine] = None):
        self.ocr_engine = ocr_engine or OCREngine()

    def extract_document(self, doc_id: str, file_path: str, max_pages: Optional[int] = None) -> ExtractedDocument:
        """
        Extracts all pages and tables from a PDF document.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")

        logger.info(f"Extracting content from PDF: {path.name} (ID: {doc_id})")
        doc = fitz.open(str(path))
        total_pages = len(doc)
        pages_to_process = min(total_pages, max_pages) if max_pages else total_pages

        extracted_pages: List[ExtractedPage] = []
        total_chars = 0

        for page_idx in range(pages_to_process):
            page_num = page_idx + 1
            page = doc[page_idx]

            # 1. Extract selectable text
            raw_text = page.get_text("text") or ""
            cleaned_text = normalize_malayalam_text(raw_text)

            # 2. Extract tables
            extracted_tables = []
            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    for t_idx, t in enumerate(tabs.tables):
                        extracted_tab = ExtractedTable(
                            page_number=page_num,
                            table_index=t_idx,
                            headers=[str(h) for h in (t.header.names if hasattr(t, "header") and t.header else [])],
                            rows=[[str(cell) for cell in row] for row in t.extract()]
                        )
                        extracted_tables.append(extracted_tab)
            except Exception as tab_err:
                logger.debug(f"Table extraction notice on page {page_num}: {tab_err}")

            # 3. Check if page is scanned or has low text
            is_scanned = len(cleaned_text.strip()) < 40
            was_ocr = False

            if is_scanned and self.ocr_engine.tesseract_installed:
                logger.info(f"Page {page_num} appears scanned. Triggering OCR engine...")
                try:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    ocr_text = self.ocr_engine.ocr_image(img, lang="mal+eng")
                    if ocr_text:
                        cleaned_text = normalize_malayalam_text(ocr_text)
                        was_ocr = True
                except Exception as ocr_err:
                    logger.warning(f"OCR error on page {page_num}: {ocr_err}")

            lang = detect_language(cleaned_text)
            char_count = len(cleaned_text)
            total_chars += char_count

            extracted_page = ExtractedPage(
                page_number=page_num,
                text=cleaned_text,
                language=lang,
                is_scanned=is_scanned,
                was_ocr=was_ocr,
                char_count=char_count,
                tables=extracted_tables
            )
            extracted_pages.append(extracted_page)

        # Detect overall document language
        combined_snippet = " ".join([p.text[:200] for p in extracted_pages[:3]])
        overall_lang = detect_language(combined_snippet)

        result = ExtractedDocument(
            document_id=doc_id,
            file_path=file_path,
            total_pages=total_pages,
            pages=extracted_pages,
            primary_language=overall_lang,
            total_characters=total_chars
        )

        # Persist extracted pages to PostgreSQL database
        self.save_extracted_content_to_db(result)

        logger.info(f"Extraction completed for {doc_id}: {len(extracted_pages)} pages, {total_chars} chars, language: {overall_lang}")
        return result

    def save_extracted_content_to_db(self, extracted: ExtractedDocument):
        """Saves page chunks into extracted_document_content table."""
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for page in extracted.pages:
                        if not page.text.strip():
                            continue
                        cur.execute(
                            """
                            INSERT INTO extracted_document_content (
                                document_id, page_number, chunk_index, content_text,
                                is_table, created_at
                            ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                            """,
                            (
                                extracted.document_id,
                                page.page_number,
                                0,
                                page.text[:10000],
                                len(page.tables) > 0
                            )
                        )

                    # Update status in scheme_documents
                    cur.execute(
                        """
                        UPDATE scheme_documents
                        SET processing_status = 'PROCESSED',
                            document_language = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                        """,
                        (extracted.primary_language, extracted.document_id)
                    )
                conn.commit()
        except Exception as e:
            logger.error(f"Error persisting extracted pages to database: {e}")
