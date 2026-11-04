"""
Sanitize Departments Registry.
Sets has_agriculture_schemes=False and investigation_status=NO_RELEVANT_SCHEMES_FOUND
for all non-agriculture departments so the crawling page and crawlers focus strictly
on genuine Agriculture & Allied Departments, Commodity Boards, and Central Schemes.
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection

AGRI_DEPT_IDS = {
    # Core State Agriculture & Allied
    "KL_AGRI_DEPT",
    "KL_AIMS_PORTAL",
    "KL_KATHIR_PORTAL",
    "KL_AHD_DEPT",
    "KL_DAIRY_DEPT",
    "KL_FISHERIES_DEPT",
    "KL_SOIL_CONS_DEPT",
    "KL_COOPERATION_DEPT",
    "KL_KSCARDB",
    "KL_KUDUMBASHREE",
    "KL_KAU_ACAD",
    "KL_VFPCK",
    "KL_HORTICORP",
    # Commodity Boards
    "BD_RUBBER",
    "BD_COCONUT",
    "BD_SPICES",
    "BD_COFFEE",
    "BD_NABARD",
    # Central Schemes
    "CEN_PM_KISAN",
    "CEN_PMFBY",
    "CEN_MIDH",
    "CEN_AIF",
    "CEN_SOIL_HEALTH",
    "CEN_PM_KUSUM",
    "CEN_RKVY",
    "CEN_MISS_KCC"
}

def update_file():
    dep_file = BASE_DIR / "registry" / "departments_data.py"
    content = dep_file.read_text(encoding="utf-8")

    # Regex to find each dictionary entry
    # For any department whose ID is NOT in AGRI_DEPT_IDS, ensure has_agriculture_schemes: False
    NON_AGRI_IDS = [
        "KL_LSGD_DEPT", "KL_RURAL_DEV", "KL_WATER_RESOURCES", "KL_FOREST_DEPT",
        "KL_SCDD_DEPT", "KL_STDD_DEPT", "KL_INDUSTRIES_DEPT", "KL_FINANCE_DEPT",
        "KL_SPB_DEPT", "KL_REVENUE", "KL_FOOD_CS", "KL_POWER", "KL_LABOUR",
        "KL_TOURISM", "KL_ENV_CLIMATE", "KL_COASTAL", "KL_AYUSH", "KL_NON_RESIDENT",
        "KL_BACKWARD_CLASSES", "KL_STATISTICS", "KL_GROUND_WATER"
    ]

    for nid in NON_AGRI_IDS:
        # Replace has_agriculture_schemes: True with False for this block
        # Pattern matching the department block
        pattern = rf'("id":\s*"{nid}",[\s\S]*?"has_agriculture_schemes":\s*)True'
        content, count = re.subn(pattern, r'\g<1>False', content)
        if count > 0:
            print(f"Updated {nid} in departments_data.py: has_agriculture_schemes -> False")

    dep_file.write_text(content, encoding="utf-8")
    print("departments_data.py updated successfully.")

def update_db():
    agri_list = list(AGRI_DEPT_IDS)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE government_departments
                SET has_agriculture_schemes = FALSE,
                    investigation_status = 'No relevant schemes found',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id != ALL(%s);
            """, (agri_list,))
            print(f"Updated PostgreSQL government_departments: {cur.rowcount} non-agri departments marked False.")

            cur.execute("""
                UPDATE government_departments
                SET has_agriculture_schemes = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s);
            """, (agri_list,))
            print(f"Verified PostgreSQL government_departments: {cur.rowcount} agri departments marked True.")
        conn.commit()

if __name__ == "__main__":
    update_file()
    update_db()
