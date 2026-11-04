"""
Specialized Crawler Adapter for Kerala Commodity Boards:
- Coconut Development Board (Kochi)
- Rubber Board India (Kottayam)
- Spices Board India (Kochi)
"""

from typing import List, Set
from bs4 import BeautifulSoup
from crawler.base_crawler import BaseCrawler, DiscoveredDocument
from crawler.keywords import match_keywords
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.commodity_boards")

COMMODITY_BOARD_TARGETS = [
    {
        "dept_id": "BD_COCONUT",
        "source_id": "SRC_BD_COCONUT",
        "name": "Coconut Development Board",
        "urls": [
            "https://coconutboard.gov.in/",
            "https://coconutboard.gov.in/index.aspx",
            "https://coconutboard.gov.in/scheme.aspx",
            "https://coconutboard.gov.in/ApplicationForms.aspx",
            "https://coconutboard.gov.in/TechnologyMission.aspx",
            "https://coconutboard.gov.in/NoticeBoard.aspx",
            "https://coconutboard.gov.in/Replanting.aspx"
        ]
    },
    {
        "dept_id": "BD_RUBBER",
        "source_id": "SRC_BD_RUBBER",
        "name": "Rubber Board India",
        "urls": [
            "https://rubberboard.gov.in/",
            "https://rubberboard.gov.in/public/schemes"
        ]
    },
    {
        "dept_id": "BD_SPICES",
        "source_id": "SRC_BD_SPICES",
        "name": "Spices Board India",
        "urls": [
            "https://indianspices.com/",
            "https://indianspices.com/schemes"
        ]
    },
    {
        "dept_id": "BD_COFFEE",
        "source_id": "SRC_BD_COFFEE",
        "name": "Coffee Board of India",
        "urls": [
            "https://coffeeboard.gov.in/",
            "https://coffeeboard.gov.in/schemes.html"
        ]
    },
    {
        "dept_id": "BD_NABARD",
        "source_id": "SRC_BD_NABARD",
        "name": "NABARD Kerala",
        "urls": [
            "https://www.nabard.org/",
            "https://www.nabard.org/content.aspx?id=597"
        ]
    }
]

class CommodityBoardsCrawlerAdapter(BaseCrawler):
    def __init__(self, target_dept_id: str = None):
        super().__init__(target_dept_id or "COMMODITY_BOARDS", f"SRC_{target_dept_id or 'COMMODITY_BOARDS'}", "https://coconutboard.gov.in/")
        self.target_dept_id = target_dept_id

    def crawl(self) -> List[DiscoveredDocument]:
        logger.info(f"Starting crawl of Commodity Boards (target={self.target_dept_id or 'ALL'})...")
        all_docs = []

        targets = [b for b in COMMODITY_BOARD_TARGETS if not self.target_dept_id or b["dept_id"] == self.target_dept_id]
        for board in targets:
            dept_id = board["dept_id"]
            source_id = board["source_id"]
            seen_urls: Set[str] = set()

            for url in board["urls"]:
                try:
                    resp = self.session.get(url, timeout=12, check_robots=False)
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link.get("href", "").strip()
                        full_url = self.normalize_url(url, href)
                        text = " ".join(link.get_text().split())

                        if self.is_document_url(full_url) and full_url not in seen_urls:
                            seen_urls.add(full_url)
                            score, matched_kws = match_keywords(f"{text} {full_url}")
                            filename = full_url.split("/")[-1].split("?")[0]
                            doc_title = text if len(text) > 4 else filename

                            doc = DiscoveredDocument(
                                title=doc_title,
                                original_url=full_url,
                                department_id=dept_id,
                                source_id=source_id,
                                file_type="pdf",
                                doc_type=self.infer_doc_type(doc_title, full_url),
                                language=self.infer_language(f"{doc_title} {text}"),
                                context_snippet=text,
                                match_score=max(score, 1),
                                matched_keywords=matched_kws
                            )
                            all_docs.append(doc)
                            logger.info(f"[{board['name']}] Found document: {doc.title} -> {doc.original_url}")
                except Exception as e:
                    logger.warning(f"Error crawling {board['name']} ({url}): {e}")

        logger.info(f"Completed Commodity Boards crawl. Total documents discovered: {len(all_docs)}")
        return all_docs
