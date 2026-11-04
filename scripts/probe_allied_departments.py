"""
Probe Allied Departments for Agricultural and Farmer Subsidies/Schemes.
Discovers genuine documents, G.O.s, circulars, and application forms.
"""

import sys
import re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from crawler.session import GovernmentSession

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TARGETS = [
    {
        "id": "KL_POWER",
        "name": "KSEB / Power Department",
        "urls": [
            "https://www.kseb.in/",
            "https://kseb.in/index.php/tariffs",
            "https://erckerala.org/regulations-orders/tariff-orders/"
        ],
        "keywords": ["tariff", "agriculture", "irrigation", "lt-v", "pump", "subsidy", "order"]
    },
    {
        "id": "KL_REVENUE",
        "name": "Revenue & Disaster Management (KSDMA)",
        "urls": [
            "https://revenue.kerala.gov.in/",
            "https://sdma.kerala.gov.in/orders-and-notifications/",
            "https://sdma.kerala.gov.in/sdrf-norms/"
        ],
        "keywords": ["sdrf", "crop", "damage", "calamity", "disaster", "loss", "farmer", "relief"]
    },
    {
        "id": "KL_FOREST",
        "name": "Forest and Wildlife Department",
        "urls": [
            "https://forest.kerala.gov.in/",
            "https://forest.kerala.gov.in/rules-regulations/",
            "https://forest.kerala.gov.in/forms/"
        ],
        "keywords": ["compensation", "crop", "wildlife", "animal", "solar fence", "fence", "depredation", "നഷ്ടപരിഹാരം"]
    },
    {
        "id": "KL_WATER",
        "name": "Water Resources / Minor Irrigation",
        "urls": [
            "https://wrd.kerala.gov.in/",
            "https://irrigation.kerala.gov.in/",
            "https://irrigation.kerala.gov.in/schemes"
        ],
        "keywords": ["minor irrigation", "lift irrigation", "canal", "pump", "farmer", "agriculture", "padasekharam"]
    },
    {
        "id": "KL_SC_DEPT",
        "name": "Scheduled Castes Development Department",
        "urls": [
            "https://scdd.kerala.gov.in/",
            "https://scdd.kerala.gov.in/schemes/",
            "https://scdd.kerala.gov.in/downloads/"
        ],
        "keywords": ["agriculture", "land", "farmer", "subsidy", "farm", "implements", "scp", "പദ്ധതി"]
    },
    {
        "id": "KL_ST_DEPT",
        "name": "Scheduled Tribes Development Department",
        "urls": [
            "https://stdd.kerala.gov.in/",
            "https://stdd.kerala.gov.in/schemes/",
            "https://stdd.kerala.gov.in/downloads/"
        ],
        "keywords": ["tribal", "agriculture", "farming", "crop", "coffee", "cardamom", "honey", "tsp", "പദ്ധതി"]
    },
    {
        "id": "KL_LSGD",
        "name": "Local Self Government Department",
        "urls": [
            "https://lsgkerala.gov.in/",
            "https://lsgkerala.gov.in/en/government-orders",
            "https://cdn.lsgkerala.gov.in/orders"
        ],
        "keywords": ["agriculture", "plan fund", "janakeeya", "panchayat", "farmer", "crop", "മണ്ണ്", "കൃഷി"]
    },
    {
        "id": "KL_INDUSTRIES",
        "name": "Industries & Commerce (PM-FME & ODOP)",
        "urls": [
            "https://industry.kerala.gov.in/",
            "https://industry.kerala.gov.in/index.php/schemes",
            "https://pmfme.mofpi.gov.in/"
        ],
        "keywords": ["pm-fme", "fme", "food", "processing", "odop", "agro", "cluster", "farmer", "subsidy"]
    },
    {
        "id": "KL_ANERT",
        "name": "ANERT (Renewable Energy / PM-KUSUM)",
        "urls": [
            "https://anert.gov.in/",
            "https://anert.gov.in/schemes",
            "https://anert.gov.in/notifications"
        ],
        "keywords": ["kusum", "solar pump", "agriculture", "pump", "dryer", "subsidy", "farmer"]
    }
]

def probe():
    session = GovernmentSession()
    for target in TARGETS:
        print(f"\n=======================================================")
        print(f"Probing {target['name']} ({target['id']})...")
        found_docs = []
        for url in target["urls"]:
            try:
                resp = session.get(url, check_robots=False)
                if resp.status_code != 200:
                    print(f"  [{resp.status_code}] Failed: {url}")
                    continue
                print(f"  [200 OK] {url} (Length: {len(resp.text)})")
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    full_url = urljoin(url, href)
                    text = a.get_text().strip()
                    combined = f"{text} {full_url}".lower()
                    if any(ext in full_url.lower() for ext in [".pdf", ".doc", ".docx"]):
                        # Check keyword match
                        matched = [k for k in target["keywords"] if k in combined]
                        if matched or any(k in combined for k in ["order", "circular", "scheme", "guideline"]):
                            found_docs.append((text or full_url.split("/")[-1], full_url, matched))
            except Exception as e:
                print(f"  Error on {url}: {e}")

        print(f"  -> Discovered {len(found_docs)} candidate documents for {target['id']}:")
        for title, doc_url, kw in found_docs[:5]:
            print(f"     * {title[:60]} -> {doc_url[:80]} (Keywords: {kw})")

if __name__ == "__main__":
    probe()
