"""
Specialized Crawler Adapter for Animal Husbandry Department, Kerala (AHD)
Portal: https://ahd.kerala.gov.in/
Discovers livestock, dairy, fodder, veterinary healthcare orders, guidelines, and insurance schemes.
"""

from typing import List, Set
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup
from crawler.base_crawler import BaseCrawler, DiscoveredDocument
from crawler.keywords import match_keywords
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.ahd")

class AnimalHusbandryCrawlerAdapter(BaseCrawler):
    def __init__(self, department_id: str = "KL_AHD_DEPT", source_id: str = "SRC_KL_AHD_DEPT", base_url: str = "https://ahd.kerala.gov.in/"):
        super().__init__(department_id, source_id, base_url)
        self.entry_points = [
            "https://ahd.kerala.gov.in/",
            "https://ahd.kerala.gov.in/en/orders-and-circulars/",
            "https://ahd.kerala.gov.in/en/government-orders/",
            "https://ahd.kerala.gov.in/en/guidelines/",
            "https://ahd.kerala.gov.in/en/forms-farmer/",
            "https://ahd.kerala.gov.in/livestock-insurance-scheme/",
            "https://ahd.kerala.gov.in/en/rinderpest-eradication-scheme-palakkad/"
        ]

    def crawl(self) -> List[DiscoveredDocument]:
        logger.info("Starting specialized crawl of Animal Husbandry Department...")
        seen_urls: Set[str] = set()

        for url in self.entry_points:
            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)

            try:
                resp = self.session.get(url, check_robots=False)
                if resp.status_code != 200:
                    logger.warning(f"AHD returned HTTP {resp.status_code} for {url}")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                for link in soup.find_all("a", href=True):
                    href = link.get("href", "").strip()
                    if not href or href == "#" or href.startswith("javascript:"):
                        continue

                    full_url = self.normalize_url(url, href)
                    text = link.get_text().strip()

                    if self.is_document_url(full_url) and full_url not in seen_urls:
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
                        logger.info(f"[AHD] Discovered document: {doc.title} -> {doc.original_url}")

            except Exception as e:
                logger.error(f"Error crawling AHD portal {url}: {e}")

        logger.info(f"Completed Animal Husbandry crawl. Discovered {len(self.discovered_documents)} documents across {len(self.visited_urls)} pages.")
        return self.discovered_documents
