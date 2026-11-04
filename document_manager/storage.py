"""
Storage abstraction for KrishiMitra AI documents.
Stores original PDFs and document versions locally in development,
with S3/MinIO compatible structure.
"""

import os
from pathlib import Path
from typing import Optional
from core.config import STORAGE_DIR
from core.logger import get_logger

logger = get_logger("krishimitra.document_manager.storage")

class DocumentStorage:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or STORAGE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_destination_path(self, department_id: str, doc_id: str, version: int, file_ext: str = "pdf") -> Path:
        """Constructs an isolated, versioned path for the document file."""
        dept_dir = self.base_dir / department_id
        dept_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{doc_id}_v{version}.{file_ext.lstrip('.')}"
        return dept_dir / filename

    def file_exists(self, path: Path) -> bool:
        return path.exists() and path.stat().st_size > 0
