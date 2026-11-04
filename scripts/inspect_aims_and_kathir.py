"""
Check all data-path elements on AIMS and inspect KATHIR HTML/APIs
"""

import sys
from pathlib import Path
from urllib.parse import urljoin, quote
import re

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.session import GovernmentSession
from bs4 import BeautifulSoup

def test_aims_data_paths():
    session = GovernmentSession()
    resp = session.get("https://aimsnew.kerala.gov.in/", timeout=25, check_robots=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    print("=" * 80)
    print("1. ALL DATA-PATH / DISPLAYDASHPDF ELEMENTS ON AIMS LANDING PAGE")
    print("=" * 80)
    
    dash_elements = soup.find_all(attrs={"data-path": True})
    print(f"Total elements with data-path: {len(dash_elements)}")
    
    for el in dash_elements:
        data_path = el.get("data-path", "").strip()
        data_id = el.get("data-id", "")
        text = el.get_text().strip().replace("\n", " ")
        full_url = urljoin("https://aimsnew.kerala.gov.in/", quote(data_path, safe="/:"))
        print(f"  - ID: {data_id} | Path: {data_path} | Text: {text}")
        print(f"    Full URL: {full_url}")
        
        # Test download of this PDF
        try:
            head_resp = session.get(full_url, timeout=15, check_robots=False)
            print(f"    HTTP Status: {head_resp.status_code} | Size: {len(head_resp.content)} bytes | Content-Type: {head_resp.headers.get('Content-Type')}")
        except Exception as e:
            print(f"    Download error: {e}")

    # Check for any other attributes containing .pdf
    print("\n--- ANY OTHER PDF REFERENCES IN AIMS HTML ---")
    raw_html = resp.text
    pdf_urls = set(re.findall(r'(/[^\s"\'<>]+\.pdf)', raw_html, re.IGNORECASE))
    for p in pdf_urls:
        print(f"  Found PDF in HTML: {p}")

def test_kathir_deep():
    session = GovernmentSession()
    print("\n" + "=" * 80)
    print("2. DEEP INSPECTION OF KATHIR (https://kathir.kerala.gov.in/)")
    print("=" * 80)
    resp = session.get("https://kathir.kerala.gov.in/", timeout=25, check_robots=False)
    print(f"Status: {resp.status_code} | Length: {len(resp.text)}")
    print("First 1000 characters of KATHIR HTML:")
    print(resp.text[:1000])

    soup = BeautifulSoup(resp.text, "html.parser")
    scripts = soup.find_all("script")
    print(f"\nTotal scripts on KATHIR: {len(scripts)}")
    for s in scripts:
        src = s.get("src")
        if src:
            print(f"  Script src: {urljoin('https://kathir.kerala.gov.in/', src)}")
        else:
            print(f"  Inline script snippet: {s.string[:200] if s.string else 'None'}")

if __name__ == "__main__":
    test_aims_data_paths()
    test_kathir_deep()
