import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT department_id, id, title, doc_type, original_url, file_path
            FROM scheme_documents
            WHERE file_path IS NOT NULL
            ORDER BY department_id;
        """)
        rows = cur.fetchall()

depts = {}
for r in rows:
    depts.setdefault(r['department_id'], []).append(r)

for d, items in depts.items():
    print(f"\n=== {d} ({len(items)} docs) ===")
    for doc in items[:8]:
        dtype = doc['doc_type'] or 'Guidelines'
        title = doc['title'][:65]
        print(f"   [{dtype}] {title}")

