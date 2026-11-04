"""
Inspect KATHIR Angular main bundle for API endpoints, scheme routes, and documents
"""

import sys
from pathlib import Path
from urllib.parse import urljoin
import re

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.session import GovernmentSession

def inspect_kathir_bundle():
    session = GovernmentSession()
    url = "https://kathir.kerala.gov.in/main.e53fd57d574aaae8.js"
    print(f"Fetching {url}...")
    resp = session.get(url, timeout=25, check_robots=False)
    print(f"Status: {resp.status_code}, Length: {len(resp.text)} chars")
    
    text = resp.text
    
    # 1. Search for API endpoints
    apis = set(re.findall(r'["\'](https?://[^"\']+|/api/[^"\']+|/v1/[^"\']+|/backend/[^"\']+)["\']', text))
    print(f"\n--- FOUND {len(apis)} API/URL REFERENCES IN KATHIR BUNDLE ---")
    for a in sorted(apis):
        if any(k in a.lower() for k in ["kerala", "agri", "scheme", "kathir", "order", "doc", "service", "gov"]):
            print(f"  * {a}")

    # 2. Search for routes
    routes = set(re.findall(r'path:\s*["\']([^"\']+)["\']', text))
    print(f"\n--- ANGULAR ROUTES IN KATHIR ({len(routes)}) ---")
    for r in sorted(routes):
        print(f"  route: /{r}")

    # 3. Search for .pdf
    pdfs = set(re.findall(r'["\']([^"\']+\.pdf)["\']', text, re.IGNORECASE))
    print(f"\n--- PDFS IN KATHIR BUNDLE ({len(pdfs)}) ---")
    for p in pdfs:
        print(f"  pdf: {p}")

if __name__ == "__main__":
    inspect_kathir_bundle()
