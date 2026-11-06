import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.database import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT count(*) as count FROM schemes WHERE department_id = 'KL_AGRI_DEPT';")
print("Current KL_AGRI_DEPT schemes count in DB:", cur.fetchone()["count"])
cur.execute("SELECT count(*) as total FROM schemes;")
print("Total schemes in DB:", cur.fetchone()["total"])

