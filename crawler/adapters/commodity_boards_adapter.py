"""
Specialized Crawler Adapter for Kerala Commodity Boards:
- Coconut Development Board (Kochi)
- Rubber Board India (Kottayam)
- Spices Board India (Kochi)
"""

import re
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

            if dept_id == "BD_RUBBER":
                rb_docs = self._crawl_rubber_board()
                all_docs.extend(rb_docs)
                continue

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

    def _crawl_rubber_board(self) -> List[DiscoveredDocument]:
        """Specialized crawler for Rubber Board India dynamic portal."""
        logger.info("Running specialized crawler for Rubber Board India...")
        docs = []
        seen = set()
        base_url = "https://rubberboard.gov.in/"

        try:
            # 1. Establish session
            self.session.get(f"{base_url}public?lang=E", timeout=15, check_robots=False)

            # 2. Scrape Approved EFC and Scheme Rules table
            post_data = {
                "item_id": "259620240901",
                "servlet": "articleview",
                "parent": "48",
                "component": "c1",
                "menuid": "850",
                "menuname": "Approved EFC and Scheme Rules, Modalities and Guidelines 2024"
            }
            res = self.session.session.post(f"{base_url}menuview", data=post_data, timeout=15, verify=False)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for tr in soup.find_all("tr"):
                    txt = " ".join(tr.get_text().split())
                    links = tr.find_all("a", href=True)
                    for a in links:
                        href = a["href"].strip()
                        if "rbfilereader" in href:
                            full_url = self.normalize_url(base_url, href)
                            if full_url not in seen:
                                seen.add(full_url)
                                title = txt if len(txt) > 4 else "Rubber Board Scheme Guidelines"
                                score, matched_kws = match_keywords(f"{title} rubber scheme subsidy")
                                docs.append(DiscoveredDocument(
                                    title=title,
                                    original_url=full_url,
                                    department_id="BD_RUBBER",
                                    source_id="SRC_BD_RUBBER",
                                    file_type="pdf",
                                    doc_type="Guidelines",
                                    language="en",
                                    context_snippet=f"{title} - Official Rubber Board scheme guidelines",
                                    match_score=max(score, 8),
                                    matched_keywords=matched_kws
                                ))
                                logger.info(f"[Rubber Board] Discovered scheme document: {title} -> {full_url}")

            # 3. Scrape c9 external link items
            r_public = self.session.get(f"{base_url}public?lang=E", timeout=15, check_robots=False)
            if r_public.status_code == 200:
                soup_pub = BeautifulSoup(r_public.text, "html.parser")
                c9_pattern = re.compile(r"gotoMenuLinkview\('[^']+',\s*'([^']+)',\s*'[^']+',\s*'c9'", re.IGNORECASE)
                for a in soup_pub.find_all("a", onclick=True):
                    m = c9_pattern.search(a["onclick"])
                    if m:
                        item_id = m.group(1)
                        item_title = " ".join(a.get_text().split()) or a.get("title", "")
                        try:
                            res_link = self.session.session.post(f"{base_url}getExternalLink", data={"item_id": item_id}, timeout=10, verify=False)
                            target_url = res_link.text.strip()
                            if "rbfilereader" in target_url or target_url.lower().endswith(".pdf"):
                                full_url = self.normalize_url(base_url, target_url)
                                if full_url not in seen:
                                    seen.add(full_url)
                                    score, matched_kws = match_keywords(f"{item_title} rubber scheme")
                                    docs.append(DiscoveredDocument(
                                        title=item_title or "Rubber Board Scheme Document",
                                        original_url=full_url,
                                        department_id="BD_RUBBER",
                                        source_id="SRC_BD_RUBBER",
                                        file_type="pdf",
                                        doc_type=self.infer_doc_type(item_title, full_url),
                                        language="en",
                                        context_snippet=f"{item_title} - Official Rubber Board document",
                                        match_score=max(score, 5),
                                        matched_keywords=matched_kws
                                    ))
                                    logger.info(f"[Rubber Board] Discovered c9 link: {item_title} -> {full_url}")
                        except Exception as e:
                            logger.warning(f"Error fetching getExternalLink for item {item_id}: {e}")

        except Exception as e:
            logger.error(f"Error crawling Rubber Board: {e}")

        return docs
