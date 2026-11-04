"""
KrishiMitra AI - End-to-End Test for Animal Husbandry Department (KL_AHD_DEPT)
Phase 4 verification:
1. Trigger crawl operation for Animal Husbandry (KL_AHD_DEPT)
2. Capture actual HTTP responses & pages visited
3. List discovered document links
4. Record download attempts, file sizes, and SHA-256 hashes
5. Verify database insertion in PostgreSQL
6. Query database records directly
7. Confirm dashboard API returns the new document count
"""

import sys
import time
import json
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.discovery_engine import DiscoveryEngine
from core.database import get_connection

def run_ahd_end_to_end_test():
    print("=" * 80)
    print("PHASE 4: ANIMAL HUSBANDRY DEPARTMENT (KL_AHD_DEPT) CRAWL TEST")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    engine = DiscoveryEngine()
    dept_id = "KL_AHD_DEPT"

    print("\n[STEP 1] Triggering crawl for department: Animal Husbandry (KL_AHD_DEPT)...")
    t0 = time.time()
    discovered_docs = engine.run_department_crawl(dept_id, auto_download=True)
    duration = round(time.time() - t0, 2)

    print(f"\n[STEP 2 & 3] Execution Complete in {duration}s")
    print(f"  - Total Discovered Documents: {len(discovered_docs)}")

    print(f"\n[STEP 4] Document Links Discovered (Sample of {min(len(discovered_docs), 10)}):")
    for i, doc in enumerate(discovered_docs[:10], 1):
        print(f"  {i}. Title: {doc.title}")
        print(f"     URL:   {doc.original_url}")
        print(f"     Type:  {doc.doc_type} | Lang: {doc.language} | Score: {doc.match_score}")

    print("\n[STEP 5, 6 & 7] Verifying PostgreSQL Records in 'scheme_documents':")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, department_id, title, original_url, file_path,
                       sha256_hash, file_size_bytes, processing_status, verification_status
                FROM scheme_documents
                WHERE department_id = %s
                ORDER BY created_at DESC;
            """, (dept_id,))
            rows = cur.fetchall()
            print(f"  --> Found {len(rows)} database records for {dept_id}:")
            for r in rows[:6]:
                print(f"    * ID: {r['id']}")
                print(f"      Title: {r['title']}")
                print(f"      URL: {r['original_url']}")
                print(f"      File on Disk: {r['file_path']} ({r['file_size_bytes']} bytes)")
                print(f"      SHA-256: {r['sha256_hash']}")
                print(f"      Status: {r['processing_status']} / {r['verification_status']}\n")

    print("[STEP 8] Confirming Dashboard API reflection:")
    try:
        url = "http://127.0.0.1:8080/api/coverage/matrix/"
        req = urllib.request.Request(url, headers={"User-Agent": "KrishiMitraVerifier/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            ahd_entry = next((item for item in data["matrix"] if item["department_id"] == dept_id), None)
            if ahd_entry:
                print(f"  --> Dashboard Coverage Matrix Entry for Animal Husbandry:")
                print(f"      Department Name: {ahd_entry['department_name']}")
                print(f"      Investigation Status: {ahd_entry['investigation_status']}")
                print(f"      Documents Discovered in Dashboard: {ahd_entry['documents_discovered']}")
                print(f"      Official Website: {ahd_entry['official_website']}")
            else:
                print(f"  [!] AHD entry not found in matrix response!")
    except Exception as e:
        print(f"  [!] Could not connect to local server: {e}")

if __name__ == "__main__":
    run_ahd_end_to_end_test()
