"""
Cleanly update registry/departments_data.py to ensure:
Only genuine agriculture, livestock, fisheries, and commodity boards have has_agriculture_schemes: True.
All line and general administration departments have has_agriculture_schemes: False and
investigation_status: InvestigationStatus.NO_RELEVANT_SCHEMES_FOUND.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

AGRI_IDS = {
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

dep_path = BASE_DIR / "registry" / "departments_data.py"
text = dep_path.read_text(encoding="utf-8")

# We will process line by line, keeping track of the current department dict
lines = text.split("\n")
output = []
current_dept = None

for line in lines:
    stripped = line.strip()
    if '"id":' in stripped:
        for word in stripped.split(","):
            if '"id":' in word:
                current_dept = word.split(":")[1].strip().strip('"').strip("'")
                break

    if '"has_agriculture_schemes":' in stripped and current_dept:
        is_agri = current_dept in AGRI_IDS
        line = line.replace('"has_agriculture_schemes": True', f'"has_agriculture_schemes": {str(is_agri)}')
        line = line.replace('"has_agriculture_schemes": False', f'"has_agriculture_schemes": {str(is_agri)}')

    if '"investigation_status":' in stripped and current_dept:
        if current_dept not in AGRI_IDS:
            line = line.replace('InvestigationStatus.DOCUMENTS_COLLECTED', 'InvestigationStatus.NO_RELEVANT_SCHEMES_FOUND')
            line = line.replace('InvestigationStatus.INVESTIGATING', 'InvestigationStatus.NO_RELEVANT_SCHEMES_FOUND')

    output.append(line)

dep_path.write_text("\n".join(output), encoding="utf-8")
print("Successfully updated registry/departments_data.py")

