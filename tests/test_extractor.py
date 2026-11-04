"""
Test for Stage 5: AI Scheme Information Extractor
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_extractor.extractor import SchemeExtractor
from core.database import get_connection

def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, department_id, title FROM scheme_documents LIMIT 1;")
            row = cur.fetchone()

    pages = [
        {
            "page_number": 1,
            "text": "Operational Guidelines for Weather Based Crop Insurance Scheme (WBCIS). Government of Kerala Agriculture Department. Objective: Financial support against crop loss."
        },
        {
            "page_number": 2,
            "text": "Beneficiaries: Small and marginal farmers in Wayanad, Idukki, and Palakkad. Eligible crops: Paddy, Banana, Pepper, Cardamom. Required documents: Aadhaar card, Land Tax Receipt, Bank Passbook."
        },
        {
            "page_number": 3,
            "text": "Subsidy: 50% premium financial assistance with maximum limit Rs 50000. Apply online at AIMS portal: https://aimsnew.kerala.gov.in/."
        }
    ]

    extractor = SchemeExtractor()
    res = extractor.extract_from_text(row["id"], row["department_id"], "Weather Based Crop Insurance Scheme (WBCIS)", pages)

    print("\n--- AI Extractor Result ---")
    print("Scheme Name:", res.scheme_name)
    print("Classification:", res.classification)
    print("Government Level:", res.government_level)
    print("Subsidy %:", res.subsidy_percentage)
    print("Subsidy Cap:", res.max_assistance_limit)
    print("Eligible Crops:", res.eligible_crops)
    print("Beneficiaries:", res.beneficiary_categories)
    print("Required Documents:", res.required_documents)
    print("Source Pages Cited:", res.source_page_numbers)
    print("Conflict Detected:", res.conflict_detected)

if __name__ == "__main__":
    main()
