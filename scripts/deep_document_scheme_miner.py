import os
import sys
import glob
from pathlib import Path
import pymupdf

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

DOCS_DIR = BASE_DIR / "storage" / "documents"

def scan_documents():
    departments = [d for d in DOCS_DIR.iterdir() if d.is_dir()]
    print(f"Scanning {len(departments)} department directories...")
    
    findings = {}
    
    for dept_folder in departments:
        dept_name = dept_folder.name
        pdf_files = list(dept_folder.glob("*.pdf"))
        print(f"\n[{dept_name}] Found {len(pdf_files)} PDF files")
        
        dept_schemes = []
        
        for pdf_path in pdf_files:
            try:
                doc = pymupdf.open(str(pdf_path))
                first_few_pages = ""
                for pno in range(min(4, len(doc))):
                    first_few_pages += doc[pno].get_text() + "\n"
                doc.close()
                
                # Check for scheme indicators
                lower_text = first_few_pages.lower()
                has_scheme_indicator = any(k in lower_text for k in [
                    "pattern of assistance", "financial assistance", "subsidy", "scheme",
                    "operational guidelines", "guidelines for", "component", "eligible", "assistance of rs"
                ])
                
                if has_scheme_indicator:
                    # Extract title or first header
                    lines = [line.strip() for line in first_few_pages.split("\n") if len(line.strip()) > 8]
                    candidate_title = lines[0] if lines else pdf_path.name
                    # Find lines mentioning subsidy or assistance
                    assistance_lines = [l for l in lines if any(k in l.lower() for k in ["subsidy", "assistance", "rs.", "rs ", "percent", "%", "lakh"])]
                    
                    dept_schemes.append({
                        "file": pdf_path.name,
                        "header": candidate_title[:120],
                        "assistance_snippet": assistance_lines[:3] if assistance_lines else []
                    })
            except Exception as e:
                pass
                
        findings[dept_name] = dept_schemes
        print(f"  -> Extracted potential scheme evidence from {len(dept_schemes)} documents.")

    return findings

if __name__ == "__main__":
    scan_documents()

