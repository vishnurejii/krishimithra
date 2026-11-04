"""
Data models for PDF and OCR extraction in KrishiMitra AI.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ExtractedTable(BaseModel):
    page_number: int
    table_index: int
    headers: List[str] = []
    rows: List[List[str]] = []
    caption: Optional[str] = None

class ExtractedPage(BaseModel):
    page_number: int
    text: str
    language: str = "en" # en, ml, bilingual
    is_scanned: bool = False
    was_ocr: bool = False
    char_count: int = 0
    tables: List[ExtractedTable] = []

class ExtractedDocument(BaseModel):
    document_id: str
    file_path: str
    total_pages: int
    pages: List[ExtractedPage] = []
    primary_language: str = "en"
    total_characters: int = 0
