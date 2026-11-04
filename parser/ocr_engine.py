"""
Malayalam & English OCR Processing Engine for KrishiMitra AI.
Integrates Tesseract OCR for scanned PDF pages and images with graceful fallback.
"""

import io
from typing import Optional
from PIL import Image
from core.logger import get_logger

logger = get_logger("krishimitra.parser.ocr")

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

class OCREngine:
    def __init__(self):
        self.available = PYTESSERACT_AVAILABLE
        self.tesseract_installed = False

        if self.available:
            try:
                # Test if tesseract executable is accessible
                ver = pytesseract.get_tesseract_version()
                self.tesseract_installed = True
                logger.info(f"Tesseract OCR is available. Version: {ver}")
            except Exception:
                logger.info("pytesseract installed, but Tesseract binary not on PATH. Fallback OCR mode active.")

    def ocr_image(self, image: Image.Image, lang: str = "mal+eng") -> str:
        """
        Runs OCR on a PIL Image with Malayalam and English language models.
        Falls back safely if binary is unavailable.
        """
        if not self.available or not self.tesseract_installed:
            logger.debug("OCR requested but Tesseract binary is not installed on system. Returning empty OCR fallback.")
            return ""

        try:
            # First try requested bilingual model (mal+eng)
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except Exception as e:
            logger.warning(f"Failed OCR with lang='{lang}': {e}. Retrying with default 'eng'...")
            try:
                text = pytesseract.image_to_string(image, lang="eng")
                return text.strip()
            except Exception as e2:
                logger.error(f"OCR fallback failed: {e2}")
                return ""
