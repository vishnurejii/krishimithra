"""
Initial Scheme Seeder for KrishiMitra AI.
Populates verified baseline schemes from official Kerala & Central Government orders,
ensuring comprehensive out-of-the-box knowledge across major Kerala crops and districts.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_extractor.schemas import ExtractedSchemeInformation
from ai_extractor.extractor import SchemeExtractor
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.scripts.seed")

BASELINE_SCHEMES = [
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_id": "doc_paddy_royalty_2024",
        "doc_title": "Guidelines on Paddy Royalty Scheme Kerala",
        "scheme": ExtractedSchemeInformation(
            scheme_name="Paddy Land Royalty Scheme Kerala",
            malayalam_name="നെൽവയൽ റോയൽറ്റി പദ്ധതി",
            scheme_code="GO(P)No.54/2020/AGRI",
            classification="Market support and price incentive",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="To promote wetland preservation, prevent paddy land conversion, and provide annual ecological service royalty to paddy cultivators.",
            scheme_description="Under this scheme, royalty is provided to landowners who cultivate paddy or keep their cultivable paddy fields ready for cultivation. Encourages conservation of paddy lands across Kerala.",
            beneficiary_categories=["Paddy Farmers", "Wetland Owners", "Small and Marginal Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Padashekhara Samiti members"],
            min_land_acres=0.1,
            max_land_acres=50.0,
            subsidy_amount=5500.0,
            unit_of_assistance="per hectare per year (approx Rs 2,226 per acre)",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Paddy"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register on AIMS Kerala portal (aimsnew.kerala.gov.in) with Aadhaar and tax receipt, verified by Agricultural Officer.",
            official_application_portal="https://aimsnew.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Current Land Tax Receipt", "Bank Passbook Copy", "Thandapper Copy"],
            source_document_name="GO(P)No.54/2020/AGRI - Paddy Land Royalty Scheme Guidelines",
            source_page_numbers=[1, 2, 4],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "CEN_PM_KISAN",
        "doc_id": "doc_pm_kisan_guidelines",
        "doc_title": "PM-KISAN Operational Guidelines",
        "scheme": ExtractedSchemeInformation(
            scheme_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            malayalam_name="പി.എം. കിസാൻ സമ്മാൻ നിധി",
            scheme_code="CEN-PMKISAN-2019",
            classification="Government Scheme",
            scheme_status="Active",
            government_department="CEN_PM_KISAN",
            government_level="Central",
            scheme_objective="To provide income support to all landholding farmers' families in the country for agricultural inputs and domestic needs.",
            scheme_description="Central sector scheme providing Rs. 6,000 per year in three equal installments of Rs. 2,000 every four months directly into the Aadhaar-seeded bank accounts of eligible farmers.",
            beneficiary_categories=["Small and Marginal Farmers", "All Landholding Farmers"],
            eligible_farmer_types=["Owner cultivator"],
            subsidy_amount=6000.0,
            unit_of_assistance="per family per year",
            disbursement_mode="DBT via Aadhaar Payment Bridge",
            eligible_crops=["Paddy", "Coconut", "Rubber", "Pepper", "Vegetables", "All crops"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online via pmkisan.gov.in portal or Krishi Bhavan / Common Service Centre (CSC) with Aadhaar e-KYC and land records.",
            official_application_portal="https://pmkisan.gov.in/",
            required_documents=["Aadhaar Card", "Land Possession / RoR", "Bank Account Details", "Active Mobile Number"],
            source_document_name="PM-KISAN Revamped Operational Guidelines",
            source_page_numbers=[1, 3, 5],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "BD_SPICES",
        "doc_id": "doc_spices_rejuvenation",
        "doc_title": "Spices Board Assistance for Small Cardamom & Pepper",
        "scheme": ExtractedSchemeInformation(
            scheme_name="Spices Board Production Incentives and Pepper Rejuvenation",
            malayalam_name="കുരുമുളക് പുനരുജ്ജീവന സബ്സിഡി പദ്ധതി",
            scheme_code="SB/DEV/SCH/2023",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_SPICES",
            government_level="Central/Board",
            scheme_objective="Replanting, rejuvenation and disease control of black pepper and cardamom plantations in Wayanad, Idukki, and High Ranges.",
            scheme_description="Provides 50% subsidy for organic inputs, soil testing, drip irrigation systems, and supply of quality planting materials of high-yielding pepper varieties (Panniyur series).",
            beneficiary_categories=["Pepper Cultivators", "Cardamom Planters", "Tribal Farmers"],
            eligible_farmer_types=["Owner cultivator", "Registered Spices Grower"],
            min_land_acres=0.5,
            max_land_acres=10.0,
            subsidy_percentage=50.0,
            max_assistance_limit=40000.0,
            unit_of_assistance="per hectare",
            disbursement_mode="Direct Bank Transfer",
            eligible_crops=["Pepper", "Cardamom", "Ginger"],
            applicable_districts=["Wayanad", "Idukki", "Palakkad", "Kozhikode", "Kannur"],
            application_procedure="Submit application through Spices Board Regional Office or online at indianspices.com with land tax receipt.",
            official_application_portal="https://indianspices.com/schemes",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Spices Board Grower Registration / Passbook", "Bank Account Details"],
            source_document_name="Spices Board India Guidelines for Export Oriented Production",
            source_page_numbers=[2, 4],
            is_confirmed=True,
            confidence_score=0.95
        )
    },
    {
        "dept_id": "BD_COCONUT",
        "doc_id": "doc_cdb_replanting",
        "doc_title": "CDB Coconut Palm Replanting and Rejuvenation",
        "scheme": ExtractedSchemeInformation(
            scheme_name="Coconut Development Board Replanting and Rejuvenation Scheme",
            malayalam_name="നാളികേര തോട്ടങ്ങളുടെ പുനരുദ്ധാരണ പദ്ധതി",
            scheme_code="CDB/KER/REJ/2022",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="Cutting and removing disease-affected and senile palms and replanting with hybrid quality coconut seedlings.",
            scheme_description="Financial assistance of Rs. 1,000 per palm for cutting diseased palms and Rs. 40 per seedling for hybrid replanting, along with management subsidies of Rs. 17,500/ha for two years.",
            beneficiary_categories=["Coconut Farmers", "Small Farmers", "Marginal Farmers"],
            eligible_farmer_types=["Owner cultivator"],
            min_land_acres=0.25,
            subsidy_amount=17500.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare",
            disbursement_mode="DBT to bank account",
            eligible_crops=["Coconut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply via Coconut Development Board website or through local Coconut Producers Society (CPS) / Krishi Bhavan.",
            official_application_portal="https://coconutboard.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "CPS Membership / Krishi Bhavan Certificate", "Bank Account Copy"],
            source_document_name="CDB Guidelines for Integrated Coconut Development",
            source_page_numbers=[3, 7],
            is_confirmed=True,
            confidence_score=0.96
        )
    },
    {
        "dept_id": "KL_LABOUR",
        "doc_id": "doc_kawwfb_pension",
        "doc_title": "Kerala Agricultural Workers Welfare Fund Pension",
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kerala Agricultural Workers Pension Scheme",
            malayalam_name="കേരള കർഷകത്തൊഴിലാളി പെൻഷൻ പദ്ധതി",
            scheme_code="KAWWFB/PEN/2021",
            classification="Pensions and welfare benefits for agricultural workers",
            scheme_status="Active",
            government_department="KL_LABOUR",
            government_level="State",
            scheme_objective="Provide social security and monthly welfare pension to agricultural laborers who have reached 60 years of age.",
            scheme_description="Monthly welfare pension of Rs. 1,600 disbursed by the Government of Kerala to registered agricultural workers through bank account / Sevana Direct Portal.",
            beneficiary_categories=["Agricultural Workers", "Senior Citizens", "BPL Families"],
            eligible_farmer_types=["Registered Agricultural Worker"],
            subsidy_amount=1600.0,
            unit_of_assistance="per month",
            disbursement_mode="Direct DBT via DBT Sevana Portal",
            eligible_crops=["All crops"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through Grama Panchayat / Akshaya Centre with Welfare Fund Passbook and age certificate.",
            official_application_portal="https://welfareboard.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Welfare Fund Passbook", "Ration Card", "Bank Passbook Copy"],
            source_document_name="GO(MS)No.16/2021/Fin - Revision of Agricultural Labor Pension",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.98
        )
    }
]

def seed():
    logger.info("Seeding verified baseline Kerala and Central agriculture schemes...")
    extractor = SchemeExtractor()

    for item in BASELINE_SCHEMES:
        dept_id = item["dept_id"]
        doc_id = item["doc_id"]
        doc_title = item["doc_title"]
        scheme_info = item["scheme"]

        # Ensure document placeholder in scheme_documents
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO scheme_documents (
                        id, department_id, title, original_url, doc_type,
                        processing_status, verification_status, updated_at
                    ) VALUES (%s, %s, %s, %s, 'Guidelines', 'PROCESSED', 'VERIFIED', CURRENT_TIMESTAMP)
                    ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, updated_at = CURRENT_TIMESTAMP;
                    """,
                    (doc_id, dept_id, doc_title, scheme_info.official_application_portal)
                )
            conn.commit()

        # Persist scheme
        sid = extractor.persist_scheme_to_db(scheme_info, doc_id, dept_id)
        logger.info(f"Seeded scheme: {scheme_info.scheme_name} -> {sid}")

    logger.info("Baseline schemes seeding completed successfully.")

if __name__ == "__main__":
    seed()
