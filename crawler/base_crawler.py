"""
Base Crawler Framework for KrishiMitra AI.
Defines data models, URL resolution, filtering, and abstract crawling behavior.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from crawler.session import GovernmentSession
from crawler.keywords import match_keywords
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.base")

class DiscoveredDocument(BaseModel):
    title: str
    original_url: str
    department_id: str
    source_id: str
    file_type: str = "pdf" # pdf, docx, html
    doc_type: str = "Guidelines" # Government Order, Circular, Guidelines, Application Form, Notification
    language: str = "en" # en, ml, bilingual
    publication_date: Optional[str] = None
    context_snippet: Optional[str] = None
    match_score: int = 1
    matched_keywords: List[str] = []
    discovered_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class BaseCrawler(ABC):
    def __init__(self, department_id: str, source_id: str, base_url: str):
        self.department_id = department_id
        self.source_id = source_id
        self.base_url = base_url
        self.session = GovernmentSession()
        self.visited_urls: Set[str] = set()
        self.discovered_documents: List[DiscoveredDocument] = []
        parsed = urlparse(base_url)
        self.allowed_domain = parsed.netloc

    def is_valid_url(self, url: str) -> bool:
        """Ensures URL belongs to the allowed domain and is not an anchor or javascript call."""
        if not url or url.startswith("#") or url.startswith("javascript:") or url.startswith("mailto:"):
            return False
        parsed = urlparse(url)
        if not parsed.netloc:
            return True
        allowed = self.allowed_domain.lower().removeprefix("www.")
        curr = parsed.netloc.lower().removeprefix("www.")
        if curr and curr != allowed and not curr.endswith("." + allowed):
            return False
        return True

    def normalize_url(self, current_page_url: str, href: str) -> str:
        """Resolves relative URLs to absolute URLs."""
        return urljoin(current_page_url, href)

    def is_document_url(self, url: str) -> bool:
        """Identifies file extension for PDFs, Word docs, etc."""
        url_lower = url.lower()
        return any(url_lower.endswith(ext) or ext in url_lower for ext in [".pdf", ".doc", ".docx", ".odt"])

    def infer_doc_type(self, title: str, url: str) -> str:
        """Infers document type from title and path."""
        combined = f"{title} {url}".lower()
        if any(k in combined for k in ["g.o", "order", "go(p)", "go(rt)", "ഉത്തരവ്"]):
            return "Government Order"
        elif any(k in combined for k in ["circular", "സർക്കുലർ"]):
            return "Circular"
        elif any(k in combined for k in ["form", "application", "അപേക്ഷ"]):
            return "Application Form"
        elif any(k in combined for k in ["amend", "revision", "ഭേദഗതി"]):
            return "Amendment"
        elif any(k in combined for k in ["notification", "വിജ്ഞാപനം"]):
            return "Notification"
        return "Guidelines"

    def infer_language(self, text: str) -> str:
        """Detects if text contains Malayalam characters (Unicode range 0D00-0D7F)."""
        has_malayalam = any(0x0D00 <= ord(c) <= 0x0D7F for c in text)
        has_english = any(c.isascii() and c.isalpha() for c in text)
        if has_malayalam and has_english:
            return "bilingual"
        elif has_malayalam:
            return "ml"
        return "en"

    @abstractmethod
    def crawl(self) -> List[DiscoveredDocument]:
        """Executes crawl logic and returns discovered documents."""
        pass
