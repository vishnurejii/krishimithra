"""
General Department Crawler for KrishiMitra AI.
Recursively crawls registered Kerala government websites up to max depth,
discovering PDFs, circulars, and scheme webpages within official domain bounds.
"""

from typing import List, Set
from bs4 import BeautifulSoup
from crawler.base_crawler import BaseCrawler, DiscoveredDocument
from crawler.keywords import match_keywords
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.general")

from typing import List, Set, Optional

class GeneralDepartmentCrawler(BaseCrawler):
    def __init__(self, department_id: str, source_id: str, base_url: str, entry_points: Optional[List[str]] = None, max_depth: int = 2, max_pages: int = 15):
        super().__init__(department_id, source_id, base_url)
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.entry_points = entry_points or [base_url]

    def crawl(self) -> List[DiscoveredDocument]:
        logger.info(f"Starting general crawl for {self.department_id} at {self.base_url} (max_pages={self.max_pages})...")
        queue = [(ep, 0) for ep in self.entry_points if ep]
        seen_urls: Set[str] = set()

        while queue and len(self.visited_urls) < self.max_pages:
            current_url, depth = queue.pop(0)
            if current_url in self.visited_urls:
                continue
            self.visited_urls.add(current_url)

            try:
                resp = self.session.get(current_url, check_robots=False)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "").strip()
                    full_url = self.normalize_url(current_url, href)
                    text = link.get_text().strip()
                    parent_text = link.parent.get_text().strip() if link.parent else ""
                    context = f"{text} {parent_text}"[:300]

                    # Check for documents
                    if self.is_document_url(full_url) and full_url not in seen_urls:
                        seen_urls.add(full_url)
                        score, matched_kws = match_keywords(f"{text} {full_url}")
                        doc_title = text if len(text) > 4 else full_url.split("/")[-1].replace("-", " ")

                        doc = DiscoveredDocument(
                            title=doc_title,
                            original_url=full_url,
                            department_id=self.department_id,
                            source_id=self.source_id,
                            file_type="pdf",
                            doc_type=self.infer_doc_type(doc_title, full_url),
                            language=self.infer_language(f"{doc_title} {context}"),
                            context_snippet=context,
                            match_score=max(score, 1),
                            matched_keywords=matched_kws
                        )
                        self.discovered_documents.append(doc)
                        logger.info(f"[{self.department_id}] Discovered document: {doc.title} -> {doc.original_url}")

                    # Check for internal links
                    elif depth < self.max_depth and self.is_valid_url(full_url) and full_url not in self.visited_urls:
                        score, _ = match_keywords(f"{text} {full_url}")
                        if score > 0 or any(k in full_url.lower() for k in ["scheme", "paddy", "farmer", "subsidy", "download", "circular", "order"]):
                            queue.append((full_url, depth + 1))

            except Exception as e:
                logger.warning(f"Error crawling {current_url}: {e}")

        logger.info(f"Finished crawling {self.department_id}. Pages visited: {len(self.visited_urls)}, Documents found: {len(self.discovered_documents)}")
        return self.discovered_documents
