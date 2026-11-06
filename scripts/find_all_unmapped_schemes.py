import sys
import os
from pathlib import Path
import pymupdf
import re

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOCS_DIR = BASE_DIR / "storage" / "documents"

def scan_folder_for_schemes(dept_name, max_files=50):
    folder = DOCS_DIR / dept_name
    if not folder.exists():
        return []
    
    files = list(folder.glob("*.pdf"))
    print(f"\n========================================================")
    print(f"Scanning {dept_name}: {len(files)} files found")
    print(f"========================================================")
    
    schemes_found = []
    
    for f in files[:max_files]:
        try:
            doc = pymupdf.open(str(f))
            text = ""
            for p in range(min(5, len(doc))):
                text += doc[p].get_text() + "\n"
            doc.close()
            
            # Search for specific scheme phrases
            lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 10]
            header = lines[0] if lines else f.name
            
            has_scheme = any(k in text.lower() for k in [
                "scheme rules for", "guidelines for", "pattern of assistance", "scheme on",
                "financial assistance for", "project on", "subsidy for", "sub component", "scale of assistance"
            ])
            
            if has_scheme:
                # Look for scale of assistance / subsidy
                subsidy_lines = [l for l in lines if any(w in l.lower() for w in ["subsidy", "assistance", "rs.", "rs ", "percent", "%", "grant", "lakh"])]
                schemes_found.append({
                    "file": f.name,
                    "title": header[:100],
                    "snippets": subsidy_lines[:3]
                })
        except Exception:
            pass

    for s in schemes_found[:12]:
        print(f"* [{s['file']}] {s['title']}")
        for sn in s['snippets']:
            print(f"    -> {sn[:100]}")
            
    return schemes_found

if __name__ == "__main__":
    scan_folder_for_schemes("BD_NABARD")
    scan_folder_for_schemes("BD_COFFEE")
    scan_folder_for_schemes("KL_KAU_ACAD")
    scan_folder_for_schemes("BD_COCONUT", max_files=40)
    scan_folder_for_schemes("BD_RUBBER")
    scan_folder_for_schemes("BD_SPICES")
    scan_folder_for_schemes("KL_AHD_DEPT", max_files=40)
