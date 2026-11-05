import sys, os, hashlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import get_connection
from scripts.register_agri_dept_schemes import AGRI_DEPT_SCHEMES

def map_docs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, original_url FROM scheme_documents WHERE department_id = 'KL_AGRI_DEPT';")
    docs = cur.fetchall()
    
    mapped_count = 0
    for doc in docs:
        title_lower = (doc["title"] or "").lower()
        url_lower = (doc["original_url"] or "").lower()
        text = title_lower + " " + url_lower

        matched_sid = None
        for entry in AGRI_DEPT_SCHEMES:
            for kw in entry["doc_keywords"]:
                if kw.lower() in text:
                    matched_sid = f"sch_{hashlib.md5(entry['scheme'].scheme_name.encode()).hexdigest()[:10]}"
                    break
            if matched_sid:
                break
        
        if matched_sid:
            cur.execute("UPDATE scheme_documents SET scheme_id = %s WHERE id = %s;", (matched_sid, doc["id"]))
            mapped_count += 1

    conn.commit()
    print(f"Mapped {mapped_count} specific documents to newly registered Agriculture Dept schemes.")
    
    cur.execute("SELECT count(*) as count FROM schemes WHERE department_id = 'KL_AGRI_DEPT';")
    total_agri = cur.fetchone()["count"]
    cur.execute("SELECT count(*) as total FROM schemes;")
    total_all = cur.fetchone()["total"]
    
    print(f"SUCCESS! Total schemes under Agriculture Department: {total_agri}")
    print(f"Total schemes across all departments in KrishiMitra: {total_all}")

if __name__ == "__main__":
    map_docs()
