"""
Purge all unwanted non-agriculture departments from PostgreSQL database.
Removes sources, crawler logs, and department master rows for any department
not in the official 27 Agriculture & Farmer Schemes registry.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection
from registry.departments_data import DEPARTMENTS_REGISTRY

KEEP_IDS = [d["id"] for d in DEPARTMENTS_REGISTRY]

def purge():
    print(f"Preserving {len(KEEP_IDS)} genuine Agriculture & Farmer departments/boards.")
    print("Purging all other departments from PostgreSQL...")

    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Delete crawler logs for unwanted sources
            cur.execute("""
                DELETE FROM crawler_logs
                WHERE source_id IN (
                    SELECT id FROM government_sources WHERE department_id != ALL(%s)
                );
            """, (KEEP_IDS,))
            print(f"Deleted crawler_logs: {cur.rowcount}")

            # 2. Delete unwanted sources
            cur.execute("""
                DELETE FROM government_sources
                WHERE department_id != ALL(%s);
            """, (KEEP_IDS,))
            print(f"Deleted government_sources: {cur.rowcount}")

            # 3. Delete unwanted departments
            cur.execute("""
                DELETE FROM government_departments
                WHERE id != ALL(%s);
            """, (KEEP_IDS,))
            print(f"Deleted government_departments: {cur.rowcount}")

            # 4. Verify remaining departments count
            cur.execute("SELECT COUNT(*) FROM government_departments;")
            remaining = cur.fetchone()["count"]
            print(f"Remaining departments in database: {remaining}")

        conn.commit()
    print("Purge completed successfully.")

if __name__ == "__main__":
    purge()

