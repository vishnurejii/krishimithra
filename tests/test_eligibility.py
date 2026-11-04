"""
Test for Stage 8: Farmer Eligibility Checker
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eligibility.models import FarmerInputProfile
from eligibility.checker import EligibilityChecker

def main():
    profile = FarmerInputProfile(
        full_name="Govindan Nambiar",
        district="Wayanad",
        taluk="Mananthavady",
        farmer_type="Small Farmer",
        total_land_acres=2.0,
        primary_crops=["Pepper", "Paddy"],
        annual_income=120000.0,
        irrigation_type="Rainfed",
        caste_category="General"
    )

    checker = EligibilityChecker()
    res = checker.evaluate_farmer(profile)

    print("\n--- Farmer Eligibility Evaluation Report ---")
    print("Farmer:", res.farmer_profile.full_name)
    print("District:", res.farmer_profile.district, "| Land:", res.farmer_profile.total_land_acres, "acres")
    print("Crops:", res.farmer_profile.primary_crops)
    print("Total Eligible Schemes Found:", res.total_matched_schemes)

    for s in res.eligible_schemes:
        print(f"\n[ELIGIBLE] {s.scheme_name} ({s.classification})")
        print("  Benefit:", s.estimated_benefit)
        print("  Documents Checklist:", s.required_documents)
        print("  Portal URL:", s.official_application_portal)
        print("  Matched Criteria:", s.matched_criteria)

if __name__ == "__main__":
    main()
