"""
Inspect AIMS user manual element and JavaScript bundles for document/PDF endpoints
"""

import sys
from pathlib import Path
from urllib.parse import urljoin
import re

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.session import GovernmentSession
from bs4 import BeautifulSoup

def inspect_aims_manuals():
    session = GovernmentSession()
    
    # 1. Fetch Landing Page and check elements matching "manual" or "പദ്ധതി"
    resp = session.get("https://aimsnew.kerala.gov.in/", timeout=25, check_robots=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    print("=" * 80)
    print("1. SEARCHING FOR MANUAL / NOTIFICATION / DOWNLOAD ELEMENTS ON AIMS LANDING PAGE")
    print("=" * 80)
    
    for tag in soup.find_all(True):
        text = tag.get_text().strip()
        if any(w in text.lower() for w in ["user manual", "user manual for employees", "വിള ഇന്‍ഷുറന്‍സ്"]):
            if tag.name in ["a", "button", "li", "span", "div"] and len(text) < 100:
                print(f"Tag: <{tag.name}> attrs: {tag.attrs} text: {text}")

    # 2. Fetch /dashboard
    print("\n" + "=" * 80)
    print("2. FETCHING https://aimsnew.kerala.gov.in/dashboard")
    print("=" * 80)
    try:
        r_dash = session.get("https://aimsnew.kerala.gov.in/dashboard", timeout=20, check_robots=False)
        print(f"Status: {r_dash.status_code} | Length: {len(r_dash.text)}")
        s_dash = BeautifulSoup(r_dash.text, "html.parser")
        dash_links = s_dash.find_all("a", href=True)
        print(f"Total <a> tags in /dashboard: {len(dash_links)}")
        for i, a in enumerate(dash_links[:20], 1):
            print(f"  {i}. {a.get('href')} | Text: {a.get_text().strip()}")
    except Exception as e:
        print(f"Dashboard error: {e}")

    # 3. Inspect JS Bundles for .pdf and api paths
    print("\n" + "=" * 80)
    print("3. INSPECTING AIMS JAVASCRIPT BUNDLES FOR PDFS & APIS")
    print("=" * 80)
    js_bundles = [
        "/build/js/navbar.38845c55.js",
        "/build/js/dynamic-dashboard.bec65098.js",
        "/build/js/common.f1c7ebd8.js",
        "/build/runtime.0923b7b8.js",
        "/build/js/homepage-chart.833f4617.js"
    ]
    for bundle in js_bundles:
        bundle_url = urljoin("https://aimsnew.kerala.gov.in/", bundle)
        try:
            r_js = session.get(bundle_url, timeout=20, check_robots=False)
            print(f"\nBundle: {bundle} (Status: {r_js.status_code}, {len(r_js.text)} bytes)")
            
            # Find any strings ending with .pdf, .docx, or containing download / document
            pdf_matches = set(re.findall(r'["\']([^"\']+\.pdf)["\']', r_js.text, re.IGNORECASE))
            if pdf_matches:
                print(f"  --> PDF matches ({len(pdf_matches)}):")
                for m in pdf_matches:
                    print(f"      * {m}")
            
            # Find api endpoints or URLs
            api_matches = set(re.findall(r'["\'](/api/[^"\']+|/dashboard/[^"\']+|/download/[^"\']+|/document/[^"\']+)["\']', r_js.text, re.IGNORECASE))
            if api_matches:
                print(f"  --> API/Path matches: {api_matches}")
        except Exception as e:
            print(f"Bundle {bundle} error: {e}")

if __name__ == "__main__":
    inspect_aims_manuals()
