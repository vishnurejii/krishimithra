"""
KrishiMitra AI - Comprehensive Crawl & Database Diagnostic Script
"""

import sys
from pathlib import Path
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import get_connection
from crawler.session import GovernmentSession
from bs4 import BeautifulSoup

def inspect_db_state():
    print("=" * 80)
    print("1. CURRENT DATABASE STATE: scheme_documents BY DEPARTMENT")
    print("=" * 80)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT department_id, COUNT(*) as doc_count,
                       COUNT(CASE WHEN file_path IS NOT NULL THEN 1 END) as downloaded_count,
                       COUNT(CASE WHEN processing_status = 'PROCESSED' THEN 1 END) as processed_count
                FROM scheme_documents
                GROUP BY department_id
                ORDER BY doc_count DESC;
            """)
            rows = cur.fetchall()
            for r in rows:
                print(f"  - Dept: {r['department_id']:<25} Total Docs: {r['doc_count']:<5} Downloaded: {r['downloaded_count']:<5} Processed: {r['processed_count']:<5}")

def inspect_portal(name: str, base_url: str, test_urls: list):
    print("\n" + "=" * 80)
    print(f"DIAGNOSTIC: {name} ({base_url})")
    print("=" * 80)
    session = GovernmentSession()

    for url in test_urls:
        try:
            print(f"\n[FETCH] GET {url} ...")
            resp = session.get(url, timeout=20, check_robots=False)
            print(f"       Status: {resp.status_code} | Size: {len(resp.content)} bytes | Final URL: {resp.url}")
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
                print(f"       Title: {title}")
                
                # Check for links
                all_links = soup.find_all("a", href=True)
                pdf_links = []
                for a in all_links:
                    h = a["href"].strip()
                    full = urljoin(url, h)
                    if any(ext in full.lower() for ext in [".pdf", ".doc", ".docx"]):
                        pdf_links.append((full, a.get_text().strip()))

                print(f"       Total <a> tags: {len(all_links)} | PDF/Doc links: {len(pdf_links)}")
                
                for full, text in pdf_links[:8]:
                    print(f"         * PDF: {full} | Text: {text[:50]}")
                
                # Sample interesting navigation links
                sublinks = []
                for a in all_links:
                    h = a["href"].strip()
                    full = urljoin(url, h)
                    if any(k in full.lower() for k in ["scheme", "order", "circular", "guideline", "service", "download", "farmer", "paddy", "insurance", "subsidy", "act"]):
                        if full not in sublinks and full != url:
                            sublinks.append(full)
                if sublinks:
                    print(f"       Potential scheme/doc sublinks ({len(sublinks)} found):")
                    for s in sublinks[:10]:
                        print(f"         - {s}")
        except Exception as e:
            print(f"       Error: {e}")

if __name__ == "__main__":
    inspect_db_state()
    
    # 1. AIMS
    inspect_portal(
        "AIMS Kerala",
        "https://aimsnew.kerala.gov.in/",
        [
            "https://aimsnew.kerala.gov.in/",
            "https://aimsnew.kerala.gov.in/paddy-royalty",
            "https://aimsnew.kerala.gov.in/crop-insurance"
        ]
    )

    # 2. KATHIR
    inspect_portal(
        "KATHIR Kerala",
        "https://kathir.kerala.gov.in/",
        [
            "https://kathir.kerala.gov.in/"
        ]
    )

    # 3. Animal Husbandry
    inspect_portal(
        "Animal Husbandry Department",
        "https://ahd.kerala.gov.in/",
        [
            "https://ahd.kerala.gov.in/",
            "https://ahd.kerala.gov.in/schemes/",
            "https://ahd.kerala.gov.in/orders/"
        ]
    )
