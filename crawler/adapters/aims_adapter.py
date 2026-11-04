"""
Specialized Crawler Adapter for AIMS Kerala (Agricultural Information Management System)
Portal: https://aimsnew.kerala.gov.in/
Discovers scheme circulars, farmer guidelines, and user manuals from HTML and HTML5 data-path attributes.
"""

from typing import List, Set
from urllib.parse import urljoin, quote, unquote
from bs4 import BeautifulSoup
from crawler.base_crawler import BaseCrawler, DiscoveredDocument
from crawler.keywords import match_keywords
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.aims")

class AIMSKeralaAdapter(BaseCrawler):
    def __init__(self, department_id: str = "KL_AIMS_PORTAL", source_id: str = "SRC_KL_AIMS_PORTAL", base_url: str = "https://aimsnew.kerala.gov.in/"):
        super().__init__(department_id, source_id, base_url)
        self.entry_points = [
            "https://aimsnew.kerala.gov.in/",
            "https://aimsnew.kerala.gov.in/dashboard",
            "https://aimsnew.kerala.gov.in/aboutUs"
        ]

    def crawl(self) -> List[DiscoveredDocument]:
        logger.info("Starting specialized crawl of AIMS Kerala portal...")
        seen_urls: Set[str] = set()

        for url in self.entry_points:
            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)

            try:
                resp = self.session.get(url, check_robots=False)
                if resp.status_code != 200:
                    logger.warning(f"AIMS portal returned status {resp.status_code} for {url}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                # 1. Standard <a> tags with href
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "").strip()
                    if not href or href == "#" or href.startswith("javascript:"):
                        continue
                    full_url = self.normalize_url(url, href)
                    text = link.get_text().strip()
                    self._check_and_add_document(full_url, text, seen_urls)

                # 2. Elements with data-path (AIMS PDF viewers and document modal triggers)
                for el in soup.find_all(attrs={"data-path": True}):
                    data_path = el.get("data-path", "").strip()
                    if not data_path:
                        continue
                    text = el.get_text().strip() or el.get("title", "").strip() or el.get("aria-label", "").strip()
                    # Clean and format path
                    safe_path = quote(unquote(data_path), safe="/:")
                    full_url = urljoin("https://aimsnew.kerala.gov.in/", safe_path)
                    self._check_and_add_document(full_url, text, seen_urls)

                # 3. Direct document patterns in HTML
                for attr_name in ["data-pdf", "data-url", "data-file"]:
                    for el in soup.find_all(attrs={attr_name: True}):
                        val = el.get(attr_name, "").strip()
                        if ".pdf" in val.lower():
                            safe_path = quote(unquote(val), safe="/:")
                            full_url = urljoin("https://aimsnew.kerala.gov.in/", safe_path)
                            text = el.get_text().strip()
                            self._check_and_add_document(full_url, text, seen_urls)

            except Exception as e:
                logger.error(f"Error crawling AIMS portal {url}: {e}")

        logger.info(f"Completed AIMS Kerala crawl. Discovered {len(self.discovered_documents)} documents across {len(self.visited_urls)} pages.")
        return self.discovered_documents

    def _check_and_add_document(self, full_url: str, text: str, seen_urls: Set[str]):
        if not self.is_document_url(full_url) or full_url in seen_urls:
            return

        seen_urls.add(full_url)
        clean_text = " ".join(text.split())
        doc_filename = unquote(full_url.split("/")[-1].split("?")[0])
        doc_title = clean_text if len(clean_text) > 4 else doc_filename.replace("-", " ").replace(".pdf", "")

        score, matched_kws = match_keywords(f"{doc_title} {full_url}")

        doc = DiscoveredDocument(
            title=doc_title,
            original_url=full_url,
            department_id=self.department_id,
            source_id=self.source_id,
            file_type="pdf",
            doc_type=self.infer_doc_type(doc_title, full_url),
            language=self.infer_language(f"{doc_title} {clean_text}"),
            context_snippet=clean_text or doc_filename,
            match_score=max(score, 1),
            matched_keywords=matched_kws
        )
        self.discovered_documents.append(doc)
        logger.info(f"[AIMS] Discovered document: {doc.title} -> {doc.original_url}")
