"""
Document parsing and OCR package for KrishiMitra AI.
"""
from parser.models import ExtractedDocument, ExtractedPage, ExtractedTable
from parser.ocr_engine import OCREngine
from parser.pdf_extractor import PDFExtractor
from parser.normalizer import normalize_malayalam_text, detect_language
