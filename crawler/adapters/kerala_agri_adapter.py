"""
Specialized Crawler Adapter for Kerala Agriculture Development and Farmers' Welfare Department
Portal: https://keralaagriculture.gov.in/
"""

from typing import List, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from crawler.base_crawler import BaseCrawler, DiscoveredDocument
from crawler.keywords import match_keywords
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.kerala_agri")

class KeralaAgriCrawlerAdapter(BaseCrawler):
    def __init__(self, department_id: str = "KL_AGRI_DEPT", source_id: str = "SRC_KL_AGRI_DEPT", base_url: str = "https://keralaagriculture.gov.in/"):
        super().__init__(department_id, source_id, base_url)
        self.entry_points = [
            "https://keralaagriculture.gov.in/",
            "https://keralaagriculture.gov.in/en/schemes/",
            "https://keralaagriculture.gov.in/en/crop-insurance-schemes/",
            "https://keralaagriculture.gov.in/en/paddy-royalty/",
            "https://keralaagriculture.gov.in/en/downloads/",
            "https://keralaagriculture.gov.in/en/acts-rules-circulars/"
        ]

    def crawl(self) -> List[DiscoveredDocument]:
        logger.info("Starting crawl of Agriculture Development and Farmers' Welfare Department...")
        queue = list(self.entry_points)
        seen_urls: Set[str] = set()

        while queue:
            current_url = queue.pop(0)
            if current_url in self.visited_urls:
                continue
            self.visited_urls.add(current_url)

            logger.info(f"Visiting page: {current_url}")
            try:
                resp = self.session.get(current_url)
                if resp.status_code != 200:
                    logger.warning(f"Skipping {current_url}: HTTP {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                # Find all links
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "").strip()
                    if not href or href.startswith("#") or href.startswith("mailto:"):
                        continue

                    full_url = self.normalize_url(current_url, href)
                    anchor_text = link.get_text().strip()
                    parent_text = link.parent.get_text().strip() if link.parent else ""
                    context = f"{anchor_text} {parent_text}"[:300]

                    # 1. Is this a PDF or document?
                    if self.is_document_url(full_url):
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            score, matched_kws = match_keywords(f"{anchor_text} {full_url}")
                            # Clean up document title
                            doc_title = anchor_text if len(anchor_text) > 4 else full_url.split("/")[-1].replace("-", " ").replace(".pdf", "")

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
                            logger.info(f"Discovered document: {doc.title} -> {doc.original_url}")

                    # 2. Is this an internal webpage link to explore further?
                    elif self.is_valid_url(full_url) and full_url not in self.visited_urls and full_url not in queue:
                        # Only follow sub-pages if they relate to schemes, downloads, orders or farmers
                        score, _ = match_keywords(f"{anchor_text} {full_url}")
                        if score > 0 or any(p in full_url.lower() for p in ["scheme", "paddy", "crop", "download", "circular", "order", "farmer", "page/"]):
                            if len(self.visited_urls) + len(queue) < 15: # Depth & politeness boundary
                                queue.append(full_url)

            except Exception as e:
                logger.error(f"Error crawling {current_url}: {e}")

        logger.info(f"Completed crawl of Karshika Keralam. Discovered {len(self.discovered_documents)} documents across {len(self.visited_urls)} pages.")
        return self.discovered_documents
