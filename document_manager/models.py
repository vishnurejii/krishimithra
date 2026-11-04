"""
Document Management Data Models for KrishiMitra AI.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class DocumentDownloadResult(BaseModel):
    document_id: str
    original_url: str
    file_path: str
    sha256_hash: str
    file_size_bytes: int
    is_duplicate: bool = False
    is_updated_version: bool = False
    previous_version: Optional[int] = None
    new_version: int = 1
    downloaded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
