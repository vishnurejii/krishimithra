import sys
from pathlib import Path
import pymupdf
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def inspect_dept(dept_name, sample_size=10):
    folder = BASE_DIR / "storage" / "documents" / dept_name
    print(f"\n========================================================")
    print(f"Inspecting {dept_name} ({len(list(folder.glob('*.pdf')))} PDF files)")
    print(f"========================================================")
    
    unique_schemes = {}
    
    for f in list(folder.glob("*.pdf"))[:sample_size*3]:
        try:
            doc = pymupdf.open(str(f))
            text = ""
            for p in range(min(4, len(doc))):
                text += doc[p].get_text() + "\n"
            doc.close()
            
            lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 10]
            header = lines[0] if lines else f.name
            
            # Find subsidy / scheme lines
            scheme_matches = [l for l in lines if any(k in l.lower() for k in [
                "scheme", "yojana", "subsidy", "assistance", "grant", "incentive", "guideline", "paddathi", "rules"
            ])]
            
            if scheme_matches:
                unique_schemes[f.name] = {
                    "header": header[:100],
                    "evidence": scheme_matches[:3]
                }
        except Exception:
            pass

    for fname, info in list(unique_schemes.items())[:sample_size]:
        print(f"* [{fname}] {info['header']}")
        for ev in info["evidence"]:
            print(f"    - {ev[:100]}")

if __name__ == "__main__":
    inspect_dept("KL_AHD_DEPT")
    inspect_dept("KL_KAU_ACAD")
    inspect_dept("BD_RUBBER")
    inspect_dept("BD_SPICES")
