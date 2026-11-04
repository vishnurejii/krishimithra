"""
Check current database state across all departments
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import get_connection

def main():
    print("=" * 80)
    print("CURRENT LIVE DATABASE STATE IN NEON POSTGRESQL (scheme_documents)")
    print("=" * 80)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.name as dept_name, sd.department_id,
                       COUNT(*) as total_documents,
                       COUNT(CASE WHEN sd.file_path IS NOT NULL THEN 1 END) as downloaded_files,
                       SUM(COALESCE(sd.file_size_bytes, 0)) as total_bytes
                FROM scheme_documents sd
                LEFT JOIN government_departments d ON sd.department_id = d.id
                GROUP BY d.name, sd.department_id
                ORDER BY total_documents DESC;
            """)
            rows = cur.fetchall()
            total_docs = 0
            total_downloaded = 0
            for r in rows:
                dept_name = r["dept_name"] or r["department_id"]
                docs = r["total_documents"]
                dl = r["downloaded_files"]
                mb = round(r["total_bytes"] / (1024 * 1024), 2)
                total_docs += docs
                total_downloaded += dl
                print(f"  - {dept_name:<60} | Dept ID: {r['department_id']:<18} | Docs: {docs:<4} | Downloaded: {dl:<4} ({mb} MB)")
            
            print("-" * 80)
            print(f"  TOTAL REGISTERED DOCUMENTS ACROSS DEPARTMENTS: {total_docs}")
            print(f"  TOTAL DOWNLOADED ON DISK: {total_downloaded}")

if __name__ == "__main__":
    main()
