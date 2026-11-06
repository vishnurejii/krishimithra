import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection

def main():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT department_id, COUNT(*) as cnt, COUNT(scheme_id) as linked
        FROM scheme_documents
        GROUP BY department_id
        ORDER BY cnt DESC;
    """)
    rows = cur.fetchall()
    print(f"{'Department ID':<20} | {'Total Docs':<10} | {'Linked Docs':<10} | {'Unlinked Docs':<12}")
    print("-" * 60)
    for r in rows:
        dept = r['department_id']
        cnt = r['cnt']
        linked = r['linked']
        unlinked = cnt - linked
        print(f"{dept:<20} | {cnt:<10} | {linked:<10} | {unlinked:<12}")

    print("\nSample Unlinked Document Titles in KL_AGRI_DEPT, BD_COCONUT, KL_AHD_DEPT, KL_KAU_ACAD, BD_RUBBER:")
    for target_dept in ['KL_AGRI_DEPT', 'BD_COCONUT', 'KL_AHD_DEPT', 'KL_KAU_ACAD', 'BD_RUBBER', 'BD_SPICES']:
        cur.execute("""
            SELECT id, title, original_url
            FROM scheme_documents
            WHERE department_id = %s AND scheme_id IS NULL AND title IS NOT NULL
            LIMIT 8;
        """, (target_dept,))
        sample = cur.fetchall()
        print(f"\n--- {target_dept} (showing {len(sample)}) ---")
        for s in sample:
            print(f"  [{s['id']}] {s['title'][:90]}")

    conn.close()

if __name__ == "__main__":
    main()

