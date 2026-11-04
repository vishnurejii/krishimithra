"""
Specialized Crawler Adapter for Central Government Agriculture Portals
Applicable to Kerala:
- PM-KISAN (https://pmkisan.gov.in/)
- PMFBY (https://pmfby.gov.in/)
- MIDH (https://midh.gov.in/)
- AIF (https://agriinfra.dac.gov.in/)
- Soil Health Card (https://soilhealth.dac.gov.in/)
"""

from typing import List, Set
from bs4 import BeautifulSoup
from crawler.base_crawler import BaseCrawler, DiscoveredDocument
from crawler.keywords import match_keywords
from core.logger import get_logger

logger = get_logger("krishimitra.crawler.central_schemes")

CENTRAL_PORTALS = [
    {
        "dept_id": "CEN_PM_KISAN",
        "source_id": "SRC_CEN_PM_KISAN",
        "name": "PM-KISAN",
        "urls": [
            "https://pmkisan.gov.in/",
            "https://pmkisan.gov.in/Documents.aspx"
        ]
    },
    {
        "dept_id": "CEN_PMFBY",
        "source_id": "SRC_CEN_PMFBY",
        "name": "PMFBY Crop Insurance",
        "urls": [
            "https://pmfby.gov.in/",
            "https://pmfby.gov.in/guidelines"
        ]
    },
    {
        "dept_id": "CEN_MIDH",
        "source_id": "SRC_CEN_MIDH",
        "name": "MIDH Horticulture Mission",
        "urls": [
            "https://midh.gov.in/",
            "https://midh.gov.in/guidelines.html"
        ]
    },
    {
        "dept_id": "CEN_AIF",
        "source_id": "SRC_CEN_AIF",
        "name": "Agriculture Infrastructure Fund",
        "urls": [
            "https://agriinfra.dac.gov.in/",
            "https://agriinfra.dac.gov.in/Home/Guidelines"
        ]
    },
    {
        "dept_id": "CEN_SOIL_HEALTH",
        "source_id": "SRC_CEN_SOIL_HEALTH",
        "name": "Soil Health Card Scheme",
        "urls": [
            "https://soilhealth.dac.gov.in/",
            "https://soilhealth.dac.gov.in/home"
        ]
    },
    {
        "dept_id": "CEN_PM_KUSUM",
        "source_id": "SRC_CEN_PM_KUSUM",
        "name": "PM-KUSUM Solar Scheme",
        "urls": [
            "https://pmkusum.mnre.gov.in/",
            "https://pmkusum.mnre.gov.in/landing-guidelines.html"
        ]
    },
    {
        "dept_id": "CEN_RKVY",
        "source_id": "SRC_CEN_RKVY",
        "name": "Rashtriya Krishi Vikas Yojana",
        "urls": [
            "https://rkvy.nic.in/",
            "https://rkvy.nic.in/static/guidelines.html"
        ]
    }
]

class CentralSchemesCrawlerAdapter(BaseCrawler):
    def __init__(self, target_dept_id: str = None):
        super().__init__(target_dept_id or "CENTRAL_SCHEMES", f"SRC_{target_dept_id or 'CENTRAL_SCHEMES'}", "https://pmkisan.gov.in/")
        self.target_dept_id = target_dept_id

    def crawl(self) -> List[DiscoveredDocument]:
        logger.info(f"Starting crawl of Central Government agriculture portals (target={self.target_dept_id or 'ALL'})...")
        all_docs = []

        targets = [p for p in CENTRAL_PORTALS if not self.target_dept_id or p["dept_id"] == self.target_dept_id]
        for portal in targets:
            dept_id = portal["dept_id"]
            source_id = portal["source_id"]
            seen_urls: Set[str] = set()

            for url in portal["urls"]:
                try:
                    resp = self.session.get(url, timeout=12, check_robots=False)
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link.get("href", "").strip()
                        full_url = self.normalize_url(url, href)
                        text = link.get_text().strip()

                        if self.is_document_url(full_url) and full_url not in seen_urls:
                            seen_urls.add(full_url)
                            score, matched_kws = match_keywords(f"{text} {full_url}")
                            doc_title = text if len(text) > 4 else full_url.split("/")[-1]

                            doc = DiscoveredDocument(
                                title=doc_title,
                                original_url=full_url,
                                department_id=dept_id,
                                source_id=source_id,
                                file_type="pdf",
                                doc_type=self.infer_doc_type(doc_title, full_url),
                                language="en",
                                context_snippet=text,
                                match_score=max(score, 1),
                                matched_keywords=matched_kws
                            )
                            all_docs.append(doc)
                            logger.info(f"[{portal['name']}] Found document: {doc.title} -> {doc.original_url}")
                except Exception as e:
                    logger.warning(f"Error crawling {portal['name']} ({url}): {e}")

        logger.info(f"Completed Central Schemes crawl. Total documents discovered: {len(all_docs)}")
        return all_docs
