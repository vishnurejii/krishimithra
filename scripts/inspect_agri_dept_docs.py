import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import get_connection

def inspect_agri():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, original_url, file_path, scheme_id 
        FROM scheme_documents 
        WHERE department_id = 'KL_AGRI_DEPT'
        ORDER BY title;
    """)
    docs = cur.fetchall()
    print(f"Total KL_AGRI_DEPT docs in DB: {len(docs)}")
    mapped = [d for d in docs if d["scheme_id"]]
    unmapped = [d for d in docs if not d["scheme_id"]]
    print(f"Mapped: {len(mapped)}, Unmapped: {len(unmapped)}\n")
    
    for i, d in enumerate(docs, 1):
        print(f"[{i:03d}] {d['title']}")
        print(f"      URL: {d['original_url']}")
        print(f"      File: {d['file_path']}")
        print(f"      Scheme ID: {d['scheme_id']}")
        print("-" * 60)

if __name__ == "__main__":
    inspect_agri()

