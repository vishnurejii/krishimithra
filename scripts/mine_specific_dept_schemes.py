import sys
from pathlib import Path
import pymupdf
import re

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def inspect_coconut_docs():
    folder = BASE_DIR / "storage" / "documents" / "BD_COCONUT"
    print("Inspecting BD_COCONUT documents...")
    
    unique_schemes = {}
    
    for f in folder.glob("*.pdf"):
        try:
            doc = pymupdf.open(str(f))
            text = ""
            for p in range(min(5, len(doc))):
                text += doc[p].get_text() + "\n"
            doc.close()
            
            # Find scheme names or projects
            matches = re.findall(r'(?:scheme for|project on|assistance for|mission on|component|yojana)[\s\w\-\(\)\'\"]{5,80}', text, re.IGNORECASE)
            for m in matches:
                clean_m = " ".join(m.split()).strip()
                if len(clean_m) > 15 and not any(k in clean_m.lower() for k in ["committee", "minutes", "held on", "under the chairmanship"]):
                    unique_schemes[clean_m] = f.name
        except Exception:
            pass

    print(f"Found {len(unique_schemes)} candidate scheme mentions in BD_COCONUT:")
    for k, v in list(unique_schemes.items())[:30]:
        print(f" - [{v}] {k}")

if __name__ == "__main__":
    inspect_coconut_docs()

