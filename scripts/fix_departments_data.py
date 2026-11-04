"""
Precise department data fixer.
Reads registry/departments_data.py line by line, detects each dictionary block by its 'id',
and sets 'has_agriculture_schemes': True if the id is in AGRI_IDS, False otherwise.
Also synchronizes PostgreSQL government_departments table.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection

AGRI_IDS = {
    # Core Kerala Agriculture & Allied
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
    # Statutory Commodity Boards
    "BD_RUBBER",
    "BD_COCONUT",
    "BD_SPICES",
    "BD_COFFEE",
    "BD_NABARD",
    # Central Agricultural Schemes
    "CEN_PM_KISAN",
    "CEN_PMFBY",
    "CEN_MIDH",
    "CEN_AIF",
    "CEN_SOIL_HEALTH",
    "CEN_PM_KUSUM",
    "CEN_RKVY",
    "CEN_MISS_KCC"
}

def fix_file():
    dep_file = BASE_DIR / "registry" / "departments_data.py"
    lines = dep_file.read_text(encoding="utf-8").splitlines()

    new_lines = []
    current_dept_id = None

    for line in lines:
        # Check if line defines an id
        if '"id":' in line:
            parts = line.split('"id":')
            raw_id = parts[1].split(",")[0].strip().strip('"').strip("'")
            current_dept_id = raw_id

        # If line contains has_agriculture_schemes
        if '"has_agriculture_schemes":' in line and current_dept_id:
            is_agri = current_dept_id in AGRI_IDS
            indent = line[:line.index('"has_agriculture_schemes":')]
            comma = "," if line.strip().endswith(",") else ""
            line = f'{indent}"has_agriculture_schemes": {str(is_agri)}{comma}'

        new_lines.append(line)

    dep_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print("Fixed registry/departments_data.py successfully.")

def fix_db():
    agri_list = list(AGRI_IDS)
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Set non-agri to False
            cur.execute("""
                UPDATE government_departments
                SET has_agriculture_schemes = FALSE,
                    investigation_status = 'No relevant schemes found',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id != ALL(%s);
            """, (agri_list,))
            print(f"PostgreSQL: {cur.rowcount} non-agri marked False.")

            # Set agri to True
            cur.execute("""
                UPDATE government_departments
                SET has_agriculture_schemes = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s);
            """, (agri_list,))
            print(f"PostgreSQL: {cur.rowcount} agri marked True.")
        conn.commit()

if __name__ == "__main__":
    fix_file()
    fix_db()
