"""
Deep inspection of AIMS Kerala (aimsnew.kerala.gov.in)
Inspects:
- Landing page HTML structure
- All hyperlinks, buttons, scripts, and endpoints
- Document repositories, guidelines, downloads, user manuals
"""

import sys
from pathlib import Path
from urllib.parse import urljoin
import re

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.session import GovernmentSession
from bs4 import BeautifulSoup

def inspect_aims_deep():
    session = GovernmentSession()
    url = "https://aimsnew.kerala.gov.in/"
    print(f"Fetching {url}...")
    resp = session.get(url, timeout=25, check_robots=False)
    print(f"HTTP Status: {resp.status_code}, Length: {len(resp.text)}")

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # 1. Print all <a> tags
    print("\n--- ALL HYPERLINKS ON AIMS LANDING PAGE ---")
    links = soup.find_all("a", href=True)
    for i, a in enumerate(links, 1):
        href = a.get("href", "").strip()
        full = urljoin(url, href)
        text = a.get_text().strip().replace("\n", " ")
        print(f"{i:2d}. Href: {href:<45} Full: {full:<50} Text: {text}")

    # 2. Check for script tags and inline javascript
    print("\n--- SCRIPT TAGS & INLINE JS ENDPOINTS ---")
    scripts = soup.find_all("script")
    for s in scripts:
        src = s.get("src")
        if src:
            print(f"  Script src: {src}")
        else:
            inline = s.string or ""
            # search for pdf or api patterns
            matches = re.findall(r'["\']([^"\']+\.(?:pdf|doc|docx|json|php|action|jsp))["\']', inline, re.IGNORECASE)
            if matches:
                print(f"  Found patterns in inline script: {matches}")

    # 3. Test well known government sub-paths on aimsnew.kerala.gov.in
    print("\n--- TESTING COMMON AIMS SUBPATHS ---")
    subpaths = [
        "guidelines", "downloads", "manual", "user-manual", "usermanual",
        "farmer-registration", "reg/farmer_registration", "documents",
        "schemes", "services", "about", "contact", "faq", "help",
        "paddy", "insurance", "orders", "circulars", "notifications",
        "assets/documents", "assets/downloads", "assets/pdf",
        "uploads", "files", "media"
    ]
    for sub in subpaths:
        test_url = urljoin(url, sub)
        try:
            r = session.get(test_url, timeout=10, check_robots=False)
            if r.status_code in [200, 301, 302]:
                print(f"  [+] Found active subpath: {test_url} -> Status {r.status_code} ({len(r.content)} bytes)")
                if r.status_code == 200:
                    s_sub = BeautifulSoup(r.text, "html.parser")
                    t_sub = s_sub.title.string.strip() if s_sub.title and s_sub.title.string else "No Title"
                    p_links = [a.get("href") for a in s_sub.find_all("a", href=True) if ".pdf" in a.get("href", "").lower()]
                    print(f"      Title: {t_sub} | PDFs: {len(p_links)}")
                    for pl in p_links[:5]:
                        print(f"        -> PDF: {urljoin(test_url, pl)}")
        except Exception as e:
            pass

if __name__ == "__main__":
    inspect_aims_deep()
