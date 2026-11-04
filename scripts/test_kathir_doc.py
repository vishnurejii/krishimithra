"""
Test KATHIR document download and endpoints
"""

import sys
from pathlib import Path
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.session import GovernmentSession

def test_kathir_doc():
    session = GovernmentSession()
    doc_path = "assets/docs/User Manual - Keralam Krishi Hub.pdf"
    url = f"https://kathir.kerala.gov.in/{quote(doc_path)}"
    print(f"Testing KATHIR Document: {url} ...")
    try:
        resp = session.get(url, timeout=20, check_robots=False)
        print(f"Status: {resp.status_code} | Size: {len(resp.content)} bytes | Content-Type: {resp.headers.get('Content-Type')}")
    except Exception as e:
        print(f"Error: {e}")

    # Check other potential docs in assets/docs/
    common_kathir_docs = [
        "assets/docs/User Manual - Keralam Krishi Hub.pdf",
        "assets/docs/Farmer_User_Manual.pdf",
        "assets/docs/KATHIR_User_Manual.pdf",
        "assets/docs/kathir_manual.pdf",
        "assets/docs/Citizen_Charter.pdf"
    ]
    for p in common_kathir_docs:
        u = f"https://kathir.kerala.gov.in/{quote(p)}"
        try:
            r = session.get(u, timeout=10, check_robots=False)
            if r.status_code == 200:
                print(f"Found KATHIR doc: {u} ({len(r.content)} bytes)")
        except Exception:
            pass

if __name__ == "__main__":
    test_kathir_doc()
