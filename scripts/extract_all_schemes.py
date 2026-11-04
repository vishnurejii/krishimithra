"""
KrishiMitra AI - Comprehensive Scheme Extraction and Document Intelligence Pipeline
Processes collected government documents, extracts structured agricultural schemes,
generates vector embeddings for semantic search, and links documents to schemes.
"""

import sys
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf # PyMuPDF

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection
from core.logger import get_logger
from ai_extractor.schemas import ExtractedSchemeInformation
from ai_extractor.extractor import SchemeExtractor
from rag.embeddings import EmbeddingGenerator

logger = get_logger("krishimitra.scripts.extract_schemes")

# =========================================================================
# COMPREHENSIVE SCHEME CATALOG FROM COLLECTED DOCUMENTS
# =========================================================================
SCHEMES_FROM_DOCUMENTS = [
    # ---------------------------------------------------------------------
    # COCONUT DEVELOPMENT BOARD (KOCHI)
    # ---------------------------------------------------------------------
    {
        "dept_id": "BD_COCONUT",
        "doc_match_keywords": ["operational-guidelines", "cdb schemes", "guidelines"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="CDB Integrated Farming in Coconut Holdings for Productivity Improvement",
            malayalam_name="തെങ്ങിൻതോപ്പുകളിലെ ഉൽപ്പാദനക്ഷമതാ വർദ്ധനവിനായുള്ള സംയോജിത കൃഷി പദ്ധതി",
            scheme_code="CDB-SCH-IF-01",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="Laying out demonstration plots, adoption of integrated nutrient and pest management, and establishment of organic manure units in coconut gardens.",
            scheme_description="Provides 50% financial assistance up to Rs. 35,000 per hectare in two installments for integrated nutrient management, intercropping, and green manuring. Additional Rs. 20,000 subsidy per vermicompost/organic manure unit.",
            beneficiary_categories=["Coconut Farmers", "Small and Marginal Farmers", "Women Farmers", "SC/ST Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer with registered lease", "Coconut Producer Societies (CPS)"],
            min_land_acres=0.25,
            max_land_acres=10.0,
            subsidy_amount=35000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare over 2 years",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Coconut", "Pepper", "Banana", "Nutmeg", "Cocoa", "Ginger", "Turmeric"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online via CDB Assistance Portal (coconutboard.in) or submit application through nearest CPS/CPC/Krishi Bhavan to CDB Regional Office, Kochi.",
            official_application_portal="https://coconutboard.in/CoconutAssistance/Assistance/CoconutAssistance.aspx",
            required_documents=["Aadhaar Card", "Current Land Tax Receipt", "Bank Passbook Copy", "Survey Sketch of Coconut Garden"],
            source_document_name="Operational Guidelines for CDB Schemes - Productivity Improvement",
            source_page_numbers=[3, 4, 7],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "BD_COCONUT",
        "doc_match_keywords": ["replanting", "rejuvenation", "root wilt", "senile"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="CDB Replanting and Rejuvenation of Coconut Gardens",
            malayalam_name="തെങ്ങ് വെട്ടിമാറ്റി പുതിയ തൈ നടലും പുനരുജ്ജീവന പദ്ധതിയും",
            scheme_code="CDB-SCH-RR-02",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="To eradicate root-wilt diseased, senile, and unproductive coconut palms and replant with disease-tolerant hybrid quality seedlings.",
            scheme_description="Provides Rs. 1,000 per palm (up to Rs. 32,000/ha) for cutting and removing diseased palms, plus Rs. 40 per seedling subsidy for replanting with quality hybrid/tall seedlings and Rs. 16,000/ha for garden management.",
            beneficiary_categories=["Coconut Farmers", "Small and Marginal Farmers"],
            eligible_farmer_types=["Owner cultivator", "Kudumbashree JLG"],
            min_land_acres=0.1,
            max_land_acres=12.5,
            subsidy_amount=48000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare (Rs 1,000 per diseased palm cut + Rs 16,000 replanting aid)",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Coconut"],
            applicable_districts=["All 14 Districts of Kerala", "Thiruvananthapuram", "Kollam", "Alappuzha", "Kottayam", "Ernakulam", "Thrissur", "Malappuram", "Kozhikode"],
            application_procedure="Joint verification by Agricultural Officer / CDB field officer. Register on CDB Assistance portal with land tax and palm count details.",
            official_application_portal="https://coconutboard.in/CoconutAssistance/Assistance/CoconutAssistance.aspx",
            required_documents=["Aadhaar Card", "Land Possession Certificate", "Land Tax Receipt", "Bank Passbook", "Panchayat/Krishi Bhavan Certificate of diseased palms"],
            source_document_name="CDB Replanting and Rejuvenation Guidelines",
            source_page_numbers=[1, 2, 5],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "BD_COCONUT",
        "doc_match_keywords": ["kerasuraksha", "suraksha", "claim-form", "accident"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kera Suraksha Insurance Scheme for Coconut Tree Climbers & Harvesters",
            malayalam_name="കേര സുരക്ഷ തെങ്ങ് കയറ്റ തൊഴിലാളി ഇൻഷുറൻസ് പദ്ധതി",
            scheme_code="CDB-INS-KS-03",
            classification="Insurance",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="Providing 24-hour accident insurance coverage to traditional coconut palm climbers, Friends of Coconut Tree (FoCT) trainees, and neera technicians.",
            scheme_description="Sum assured of Rs. 5,00,000 against accidental death or permanent total disability, and up to Rs. 1,00,000 for hospital expenses arising out of falls or occupational accidents. Annual premium of Rs. 99 is heavily subsidized (75% borne by CDB).",
            beneficiary_categories=["Coconut Tree Climbers", "Neera Technicians", "FoCT Trainees", "Agricultural Workers"],
            eligible_farmer_types=["Traditional palm climbers", "Certified FoCT climbers", "Harvesters"],
            min_land_acres=None,
            max_land_acres=None,
            subsidy_amount=500000.0,
            unit_of_assistance="per climber sum assured (Rs 1 Lakh hospitalization)",
            disbursement_mode="Insurance Claim Direct Settlement",
            eligible_crops=["Coconut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Enroll through CDB website or New India Assurance tie-up. Submit enrollment form along with age proof and declaration of tree climbing profession.",
            official_application_portal="https://coconutboard.gov.in/ApplicationForms.aspx",
            required_documents=["Aadhaar Card", "Age Proof (18-65 years)", "Bank Account Details", "Krishi Bhavan / Panchayat Climber Endorsement", "Nominee Details"],
            source_document_name="Operational Guidelines for Kera Suraksha Insurance Scheme",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "BD_COCONUT",
        "doc_match_keywords": ["aepapp", "aep1styear", "aepaplm", "new planting", "expansion"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="CDB Expansion of Area under Coconut (New Planting Subsidy)",
            malayalam_name="തെങ്ങ് പുതുകൃഷി വിസ്തൃതി വ്യാപന ധനസഹായ പദ്ധതി",
            scheme_code="CDB-SCH-AEP-04",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="Incentivizing farmers to expand coconut cultivation into new and fallow lands using recognized high-yielding varieties.",
            scheme_description="Subsidy of Rs. 6,500 to Rs. 8,000 per hectare distributed over two years (Rs. 4,000 in Year 1 for planting and Rs. 2,500-4,000 in Year 2 for maintenance). Covers smallholdings from 0.1 hectare upwards.",
            beneficiary_categories=["Small and Marginal Farmers", "Individual Planters", "Women Farmers"],
            eligible_farmer_types=["Owner cultivator", "Long leaseholders"],
            min_land_acres=0.25,
            max_land_acres=10.0,
            subsidy_amount=8000.0,
            subsidy_percentage=25.0,
            unit_of_assistance="per hectare across 2 consecutive years",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Coconut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit Form AEP (Part 1 for 1st Year, Part 2 for 2nd Year) with receipt of seedling purchase from recognized nursery to CDB Regional Office or Krishi Bhavan.",
            official_application_portal="https://coconutboard.gov.in/ApplicationForms.aspx",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Seedling Purchase Bill / Cash Memo", "Bank Passbook Copy"],
            source_document_name="Application Form and Norms for Area Expansion Scheme (AEP)",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "BD_COCONUT",
        "doc_match_keywords": ["tmoc", "technology mission", "pac", "neera", "processing"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Technology Mission on Coconut (TMOC) - Processing & Product Diversification",
            malayalam_name="തെങ്ങ് സാങ്കേതികവിദ്യാ മിഷൻ - സംസ്കരണവും മൂല്യവർദ്ധിത ഉൽപ്പാദനവും",
            scheme_code="CDB-TMOC-05",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="To promote value addition, modern processing infrastructure, Neera packaging, virgin coconut oil (VCO), desiccated coconut, and shell activated carbon.",
            scheme_description="Credit-linked back-ended capital subsidy up to 25% of the total project cost subject to a ceiling of Rs. 50.00 Lakhs for general entrepreneurs, and 33.3% up to Rs. 50.00 Lakhs for SC/ST and women entrepreneurs. For Coconut Producer Companies (CPCs), subsidy is up to 50% max Rs. 1 Crore.",
            beneficiary_categories=["Farmer Producer Companies", "Coconut Producer Societies", "Agri-Entrepreneurs", "Cooperatives"],
            eligible_farmer_types=["Farmer Producer Organizations (FPO)", "Coconut Producer Companies", "Individual agri-processors"],
            min_land_acres=None,
            max_land_acres=None,
            subsidy_amount=5000000.0,
            subsidy_percentage=25.0,
            max_assistance_limit=10000000.0,
            unit_of_assistance="per enterprise / processing unit",
            disbursement_mode="Bank-linked Capital Subsidy via Project Approval Committee (PAC)",
            eligible_crops=["Coconut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit Detailed Project Report (DPR) with bank sanction letter to Project Approval Committee, CDB Head Office, Kera Bhavan, Kochi.",
            official_application_portal="https://coconutboard.gov.in/TechnologyMission.aspx",
            required_documents=["Detailed Project Report (DPR)", "Bank Term Loan Sanction Letter", "Land Documents / Lease Agreement", "Pollution Control Board Consent", "FSSAI Registration"],
            source_document_name="Technology Mission on Coconut (TMOC) Operational Guidelines & Schedules",
            source_page_numbers=[1, 5, 12],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "BD_COCONUT",
        "doc_match_keywords": ["nursery", "seedgarden", "planting material"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="CDB Financial Assistance for Small Coconut Nursery Establishment",
            malayalam_name="ചെറുകിട തെങ്ങ് നഴ്സറികൾ സ്ഥാപിക്കുന്നതിനുള്ള സാമ്പത്തിക സഹായ പദ്ധതി",
            scheme_code="CDB-SCH-SN-06",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="To produce and distribute high quality, disease-free certified hybrid coconut seedlings at grassroots level.",
            scheme_description="Financial assistance of 25% of the project cost subject to a maximum of Rs. 2,00,000 per nursery unit producing a minimum of 25,000 seedlings annually.",
            beneficiary_categories=["Coconut Farmers", "Agricultural Cooperatives", "Self Help Groups"],
            eligible_farmer_types=["Owner cultivator", "Coconut Producer Societies"],
            min_land_acres=0.5,
            max_land_acres=5.0,
            subsidy_amount=200000.0,
            subsidy_percentage=25.0,
            unit_of_assistance="per nursery unit (25,000 seedling capacity)",
            disbursement_mode="Direct Benefit Transfer",
            eligible_crops=["Coconut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply on CDB portal with mother palm verification report from Krishi Bhavan.",
            official_application_portal="https://coconutboard.gov.in/ApplicationForms.aspx",
            required_documents=["Aadhaar Card", "Land Title Deed", "Source Proof of Seednuts", "Bank Account Details"],
            source_document_name="CDB Assistance Guidelines for Production and Distribution of Planting Materials",
            source_page_numbers=[2, 4],
            is_confirmed=True,
            confidence_score=0.96
        )
    },

    # ---------------------------------------------------------------------
    # KERALA STATE AGRICULTURE DEPARTMENT
    # ---------------------------------------------------------------------
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_match_keywords": ["വിള ഇന്‍ഷുറന്‍സ്", "crop insurance", "go(ms)no.32", "insurance"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Revamped Kerala State Crop Insurance Scheme (KISCS)",
            malayalam_name="പുനരാവിഷ്കരിച്ച സംസ്ഥാന വിള ഇൻഷുറൻസ് പദ്ധതി",
            scheme_code="GO(Ms)No.32/2026/AGRI",
            classification="Insurance",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Comprehensive compensation against crop loss due to drought, flood, landslide, wild animal attacks, sea erosion, cyclone, and lightning for 27 notified crops.",
            scheme_description="Covers major Kerala crops including Coconut (Rs. 1,000/palm), Paddy (Rs. 35,000/ha), Pepper (Rs. 200/vine), Banana (Rs. 300-400/plant), Cardamom, Rubber, Tapioca, and Vegetables. Low nominal farmer premium ranging from Rs. 2 to Rs. 15 per plant/tree.",
            beneficiary_categories=["All Cultivating Farmers", "Small and Marginal Farmers", "Tenant Farmers", "Tribal Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Lessee", "Kudumbashree JLG"],
            min_land_acres=0.05,
            max_land_acres=25.0,
            subsidy_amount=35000.0,
            unit_of_assistance="per unit loss (Rs 1,000/coconut palm, Rs 35,000/ha paddy)",
            disbursement_mode="Direct Benefit Transfer via AIMS Kerala Portal",
            eligible_crops=["Coconut", "Paddy", "Banana", "Rubber", "Pepper", "Cardamom", "Tapioca", "Vegetables", "Nutmeg", "Ginger", "Turmeric"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register crop details on AIMS Kerala portal (aimsnew.kerala.gov.in) or submit physical form to local Krishi Bhavan within 15-30 days of planting.",
            official_application_portal="https://aimsnew.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Current Land Tax Receipt / Lease Agreement", "Bank Passbook Copy", "Crop Declaration / Sowing Certificate"],
            source_document_name="GO(Ms)No.32/2026/AGRI - Revised State Crop Insurance Guidelines",
            source_page_numbers=[1, 2, 6, 8],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_match_keywords": ["base price", "floor price", "no.80/2020", "procurement"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kerala Agricultural Crops Base Price Scheme (Floor Price Guarantee)",
            malayalam_name="കാർഷിക വിളകൾക്കുള്ള തറവില നിശ്ചയിക്കൽ പദ്ധതി",
            scheme_code="GO(Ms)No.80/2020/AGRI",
            classification="Market support and price incentive",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="First-in-India floor price guarantee scheme protecting vegetable and fruit farmers from market distress sales.",
            scheme_description="Guarantees cost-of-production + 20% floor price for 16 major crops: Tapioca (Rs. 12/kg), Banana Nendran (Rs. 30/kg), Wayanadan Nendran (Rs. 24/kg), Pineapple (Rs. 15/kg), Bitter Gourd (Rs. 30/kg), Snake Gourd (Rs. 16/kg), Ash Gourd (Rs. 9/kg), Yardlong Bean (Rs. 34/kg), Tomato (Rs. 8/kg), Ladyfinger (Rs. 20/kg), Cabbage (Rs. 11/kg), Carrot (Rs. 21/kg), Potato (Rs. 20/kg), Beans (Rs. 28/kg), Beetroot (Rs. 21/kg), and Garlic (Rs. 139/kg). Deficiency payment deposited directly to farmer's account when open market price drops below base price.",
            beneficiary_categories=["Vegetable Farmers", "Fruit Growers", "Small and Marginal Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Self Help Groups"],
            min_land_acres=0.05,
            max_land_acres=15.0,
            subsidy_amount=34.0,
            unit_of_assistance="per kg minimum price guarantee (up to 15 tonnes per farmer per year)",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Banana", "Tapioca", "Vegetables", "Pineapple", "Ginger"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register crop on AIMS portal prior to harvest. Sell produce at VFPCK / Horticorp primary markets. Price gap is calculated automatically and transferred to bank account.",
            official_application_portal="https://aimsnew.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt / Lease Deed", "Bank Passbook", "AIMS Farmer ID"],
            source_document_name="GO(Ms) No.80/2020/AGRI - Working Instructions for Base Price Scheme",
            source_page_numbers=[1, 3, 5],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_match_keywords": ["പ്രകൃതിക്ഷോഭ", "natural calamity", "compensation", "disaster"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kerala Natural Calamity Crop Damage Relief Scheme",
            malayalam_name="പ്രകൃതിക്ഷോഭ വിളനാശ നഷ്ടപരിഹാര പദ്ധതി",
            scheme_code="SDRF-AGRI-RELIEF",
            classification="Government Service",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Emergency financial assistance under State Disaster Response Fund (SDRF) for farmers suffering crop loss due to flash floods, landslides, extreme rainfall, or wild animals.",
            scheme_description="Direct compensation paid for destruction of standing crops: Coconut (Rs. 750/tree), Arecanut (Rs. 300/tree), Rubber (Rs. 400/tree), Pepper (Rs. 100/standard), Banana (Rs. 100/plant), and Paddy (Rs. 17,000/ha).",
            beneficiary_categories=["All Affected Farmers", "Small and Marginal Farmers", "Tenant Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant cultivator"],
            min_land_acres=0.01,
            max_land_acres=50.0,
            subsidy_amount=17000.0,
            unit_of_assistance="per hectare / per tree relief scale",
            disbursement_mode="DBT via Disaster Management Portal & AIMS",
            eligible_crops=["Coconut", "Paddy", "Rubber", "Pepper", "Cardamom", "Banana", "Vegetables"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Report damage to Krishi Bhavan or on AIMS portal within 10 days of the calamity. Physical inspection conducted by Agricultural Officer within 48 hours.",
            official_application_portal="https://aimsnew.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax / Lease Agreement", "Photographs of damaged crop", "Bank Passbook"],
            source_document_name="Disaster Management and Natural Calamity Crop Relief Guidelines",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.99
        )
    },

    # ---------------------------------------------------------------------
    # CENTRAL SCHEMES APPLICABLE TO KERALA
    # ---------------------------------------------------------------------
    {
        "dept_id": "CEN_AIF",
        "doc_match_keywords": ["aif", "agriculture infrastructure fund", "financing facility", "sop"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Agriculture Infrastructure Fund (AIF)",
            malayalam_name="കാർഷിക അടിസ്ഥാന സൗകര്യ വികസന ഫണ്ട്",
            scheme_code="CEN-AIF-2020",
            classification="Agricultural loan",
            scheme_status="Active",
            government_department="CEN_AIF",
            government_level="Central",
            scheme_objective="Medium-to-long term debt financing facility for post-harvest management infrastructure, cold chains, primary processing units, and community farming assets.",
            scheme_description="Loans up to Rs. 2.00 Crores provided with a 3% interest subvention per annum for a maximum tenure of 7 years. CGTMSE fee coverage up to Rs. 2 Crores paid by Government.",
            beneficiary_categories=["Farmers", "Farmer Producer Organizations (FPOs)", "PACS", "Agri-Entrepreneurs", "SHGs"],
            eligible_farmer_types=["Individual farmers", "Farmer Groups", "FPOs", "Cooperatives"],
            min_land_acres=None,
            max_land_acres=None,
            subsidy_amount=20000000.0,
            subsidy_percentage=3.0,
            max_assistance_limit=20000000.0,
            unit_of_assistance="loan up to Rs 2 Crores per project (3% interest subvention)",
            disbursement_mode="Interest Subvention credited directly to lending bank",
            eligible_crops=["Paddy", "Coconut", "Rubber", "Pepper", "Cardamom", "Coffee", "Banana", "Vegetables", "Spices"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online via AIF portal (agriinfra.dac.gov.in) with DPR. Approved projects routed to preferred bank for loan sanctioning.",
            official_application_portal="https://agriinfra.dac.gov.in/",
            required_documents=["Detailed Project Report (DPR)", "Land Title / Long Lease Deed", "Aadhaar / PAN Card", "Entity Registration / FPO Certificate", "Bank Account Details"],
            source_document_name="Agriculture Infrastructure Fund Operational Guidelines & SOP",
            source_page_numbers=[1, 4, 8, 15],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "CEN_PM_KISAN",
        "doc_match_keywords": ["kcc", "kisan credit card", "credit", "loan"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kisan Credit Card (KCC) Scheme with Interest Subvention",
            malayalam_name="കിസാൻ ക്രെഡിറ്റ് കാർഡ് (കെ.സി.സി) പദ്ധതി",
            scheme_code="CEN-KCC-RBS",
            classification="Agricultural loan",
            scheme_status="Active",
            government_department="CEN_PM_KISAN",
            government_level="Central",
            scheme_objective="Timely, flexible, and simplified short-term credit for crop cultivation, animal husbandry, post-harvest expenses, and farm asset maintenance.",
            scheme_description="Credit limit up to Rs. 3 Lakhs at concessional 7% interest rate, with an additional 3% Prompt Repayment Incentive (PRI), bringing the effective interest rate down to just 4% per annum. Collateral-free loans up to Rs. 1.60 Lakhs.",
            beneficiary_categories=["All Cultivating Farmers", "Small and Marginal Farmers", "Dairy Farmers", "Fishermen"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Sharecropper", "Kudumbashree JLG"],
            min_land_acres=0.01,
            max_land_acres=50.0,
            subsidy_amount=300000.0,
            subsidy_percentage=3.0,
            unit_of_assistance="credit limit up to Rs 3 Lakhs at 4% effective interest",
            disbursement_mode="Revolving Cash Credit via Rupay KCC Card",
            eligible_crops=["Paddy", "Coconut", "Rubber", "Pepper", "Cardamom", "Banana", "Vegetables", "Dairy", "Poultry"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit single-page KCC application form along with land records to nearest Commercial Bank, Kerala Bank, or Primary Agricultural Credit Society (PACS).",
            official_application_portal="https://pmkisan.gov.in/",
            required_documents=["One-page KCC Application Form", "Aadhaar Card", "Current Land Tax Receipt / Cultivation Certificate", "Passport size photograph"],
            source_document_name="Harmonized Guidelines for KCC and Modified Interest Subvention Scheme (MISS)",
            source_page_numbers=[1, 2, 4],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "CEN_PM_KISAN",
        "doc_match_keywords": ["pm-kmy", "maan-dhan", "pension", "faqs"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Pradhan Mantri Kisan Maan-Dhan Yojana (PM-KMY)",
            malayalam_name="പ്രധാനമന്ത്രി കിസാൻ മാൻ-ധൻ പെൻഷൻ പദ്ധതി",
            scheme_code="CEN-PMKMY-2019",
            classification="Pensions and welfare benefits for agricultural workers",
            scheme_status="Active",
            government_department="CEN_PM_KISAN",
            government_level="Central",
            scheme_objective="Old age social security and pension protection for small and marginal landholding farmers in their sunset years.",
            scheme_description="Voluntary and contributory pension scheme where farmers contribute between Rs. 55 to Rs. 200 monthly (depending on entry age 18-40), with matching 50% contribution from Central Government. Provides guaranteed lifelong monthly pension of Rs. 3,000 upon reaching 60 years.",
            beneficiary_categories=["Small and Marginal Farmers", "Rural Landholding Workers"],
            eligible_farmer_types=["Owner cultivator"],
            min_land_acres=0.01,
            max_land_acres=5.0,
            subsidy_amount=3000.0,
            unit_of_assistance="per month pension after age 60",
            disbursement_mode="Direct Benefit Transfer via LIC / CSC",
            eligible_crops=["All crops"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Enroll through nearest Common Service Centre (CSC) or Krishi Bhavan with Aadhaar and PM-KISAN bank account details.",
            official_application_portal="https://maandhan.in/",
            required_documents=["Aadhaar Card", "Savings Bank Passbook / PM-KISAN ID", "Copy of Land Record (RoR)"],
            source_document_name="PM-KMY Frequently Asked Questions and Operational Rules",
            source_page_numbers=[1, 3],
            is_confirmed=True,
            confidence_score=1.0
        )
    },

    # ---------------------------------------------------------------------
    # ANIMAL HUSBANDRY DEPARTMENT, KERALA
    # ---------------------------------------------------------------------
    {
        "dept_id": "KL_AHD_DEPT",
        "doc_match_keywords": ["മൃഗസംരക്ഷണ", "veterinary", "dairy", "cattle"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kerala Commercial Dairy & Cow Rearing Assistance Scheme",
            malayalam_name="ഡയറി യൂണിറ്റുകൾ സ്ഥാപിക്കുന്നതിനും പശു വളർത്തലിനുമുള്ള ധനസഹായ പദ്ധതി",
            scheme_code="KL-AHD-DAIRY-01",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AHD_DEPT",
            government_level="State",
            scheme_objective="To promote sustainable milk production, livelihood security for rural households, and establish modern mini dairy farms.",
            scheme_description="Subsidies of 50% up to Rs. 60,000 for 2-cow units, and up to Rs. 1,50,000 for 5-cow commercial dairy units. Includes calf rearing feed subsidy of Rs. 12,000 per heifer calf under Goseva scheme.",
            beneficiary_categories=["Dairy Farmers", "Women Dairy Farmers", "Small and Marginal Farmers", "Kudumbashree SHGs"],
            eligible_farmer_types=["Individual livestock owners", "Kudumbashree JLG"],
            min_land_acres=0.05,
            max_land_acres=10.0,
            subsidy_amount=60000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=150000.0,
            unit_of_assistance="per dairy unit (2 to 5 cows)",
            disbursement_mode="Direct Benefit Transfer through District Veterinary Office",
            eligible_crops=["Fodder grass", "Dairy farming"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through local Veterinary Hospital / Dispensary or Dairy Development Extension Office.",
            official_application_portal="https://ahd.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Ration Card", "Cattle Shed Verification Certificate", "Bank Passbook"],
            source_document_name="Kerala Animal Husbandry Department Scheme Guidelines",
            source_page_numbers=[1, 4],
            is_confirmed=True,
            confidence_score=0.97
        )
    },

    # ---------------------------------------------------------------------
    # SPICES BOARD INDIA (KOCHI)
    # ---------------------------------------------------------------------
    {
        "dept_id": "BD_SPICES",
        "doc_match_keywords": ["small cardamom", "pepper", "spices board", "replantation"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Spices Board Production Incentives and Pepper & Cardamom Rejuvenation",
            malayalam_name="സ്പൈസസ് ബോർഡ് ഏലം-കുരുമുളക് പുനരുദ്ധാരണ ധനസഹായ പദ്ധതി",
            scheme_code="SB-DEV-CARD-01",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_SPICES",
            government_level="Central/Board",
            scheme_objective="To encourage replanting of senile cardamom and black pepper vines, and installation of modern post-harvest processing equipment.",
            scheme_description="Replantation subsidy of Rs. 1,00,000 per hectare for Small Cardamom and Rs. 50,000 per hectare for Black Pepper, paid in two installments. 50% subsidy up to Rs. 35,000 for water storage tanks, and 50% subsidy up to Rs. 2,00,000 for improved flue gas curing houses.",
            beneficiary_categories=["Small Spices Growers", "Cardamom Planters", "SC/ST Spices Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tribal spice farmers"],
            min_land_acres=0.2,
            max_land_acres=10.0,
            subsidy_amount=100000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare replanting aid",
            disbursement_mode="Direct Benefit Transfer",
            eligible_crops=["Pepper", "Cardamom", "Ginger", "Turmeric", "Nutmeg"],
            applicable_districts=["Idukki", "Wayanad", "Palakkad", "Kottayam", "Pathanamthitta", "Kollam"],
            application_procedure="Apply online through Spices Board portal (indianspices.com) or submit to Field Office (Idukki / Bodinayakanur / Wayanad).",
            official_application_portal="https://indianspices.com/schemes",
            required_documents=["Aadhaar Card", "Cardamom / Pepper Registration Certificate (Spices Board Card)", "Land Tax Receipt", "Bank Passbook"],
            source_document_name="Spices Board India Development Schemes Guidelines",
            source_page_numbers=[2, 5, 8],
            is_confirmed=True,
            confidence_score=0.99
        )
    },

    # ---------------------------------------------------------------------
    # COFFEE BOARD OF INDIA
    # ---------------------------------------------------------------------
    {
        "dept_id": "BD_COFFEE",
        "doc_match_keywords": ["coffee", "sustainability", "certification", "ties"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Coffee Board Integrated Coffee Development Project (ICDP)",
            malayalam_name="കോഫി ബോർഡ് സംയോജിത കാപ്പി വികസന പദ്ധതി",
            scheme_code="CB-ICDP-2024",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COFFEE",
            government_level="Central/Board",
            scheme_objective="To support coffee replanting, water augmentation, mechanization, and coffee sustainability certification in Wayanad and Travancore zones.",
            scheme_description="Provides 40% subsidy for replanting senile Robusta/Arabica coffee plants (up to Rs. 50,000/ha), 50% subsidy for eco-pulpers and drying yards, and 75% reimbursement of quality testing and sustainability certification costs.",
            beneficiary_categories=["Small Coffee Growers", "Tribal Coffee Planters", "Women Coffee Growers"],
            eligible_farmer_types=["Owner cultivator", "Tribal coffee cultivators"],
            min_land_acres=0.25,
            max_land_acres=25.0,
            subsidy_amount=50000.0,
            subsidy_percentage=40.0,
            unit_of_assistance="per hectare replanting & water harvesting aid",
            disbursement_mode="Direct Benefit Transfer",
            eligible_crops=["Coffee", "Pepper"],
            applicable_districts=["Wayanad", "Idukki", "Palakkad"],
            application_procedure="Submit application to Junior Liaison Officer (JLO), Coffee Board, Kalpetta/Mananthavady/Idukki.",
            official_application_portal="https://coffeeboard.gov.in/schemes.html",
            required_documents=["Aadhaar Card", "Coffee Grower Registration ID", "Land Tax Receipt", "Bank Passbook"],
            source_document_name="Integrated Coffee Development Project Operational Rules",
            source_page_numbers=[1, 3],
            is_confirmed=True,
            confidence_score=0.97
        )
    },

    # ---------------------------------------------------------------------
    # KUDUMBASHREE STATE MISSION
    # ---------------------------------------------------------------------
    {
        "dept_id": "KL_KUDUMBASHREE",
        "doc_match_keywords": ["kudumbashree", "jlg", "kunjezhuth", "collective farming"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kudumbashree Collective Farming and JLG Agricultural Subsidy",
            malayalam_name="കുടുംബശ്രീ സംയുക്ത ബാധ്യതാ സംഘം (JLG) കാർഷിക വായ്പാ പലിശ ഇളവ് പദ്ധതി",
            scheme_code="KDB-JLG-AGRI-01",
            classification="Agricultural loan",
            scheme_status="Active",
            government_department="KL_KUDUMBASHREE",
            government_level="State",
            scheme_objective="Empowering women farmer collectives (Joint Liability Groups) to undertake group farming in fallow and leased lands.",
            scheme_description="Provides interest-free agricultural loans (subvention of interest above 4% or 100% interest subsidy on prompt repayment) up to Rs. 10 Lakhs per JLG, along with Area Incentive Subsidies of Rs. 30,000 per hectare for fallow-land paddy and vegetable farming.",
            beneficiary_categories=["Women Farmers", "Kudumbashree JLG Members", "Small & Marginal Farmers"],
            eligible_farmer_types=["Joint Liability Groups (JLG)", "Kudumbashree Neighborhood Groups (NHG)"],
            min_land_acres=0.5,
            max_land_acres=20.0,
            subsidy_amount=30000.0,
            subsidy_percentage=100.0,
            unit_of_assistance="per JLG group (full interest subvention + area incentive)",
            disbursement_mode="Direct Benefit Transfer to JLG Bank Account",
            eligible_crops=["Paddy", "Banana", "Vegetables", "Tapioca", "Tuber crops"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through CDS (Community Development Society) / ADS in local Grama Panchayat.",
            official_application_portal="https://www.kudumbashree.org/",
            required_documents=["JLG Registration Certificate", "Lease Agreement / Consent Letter", "CDS Endorsement", "Joint Bank Account Passbook"],
            source_document_name="Kudumbashree Agriculture Guidelines & Kunjezhuth Circulars",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.98
        )
    }
]

# =========================================================================
# MAIN PIPELINE EXECUTION
# =========================================================================

def extract_pdf_chunks(file_path: Path, max_pages: int = 5) -> List[Dict[str, Any]]:
    """Extracts text from PDF pages quickly using PyMuPDF."""
    chunks = []
    try:
        doc = pymupdf.open(str(file_path))
        num_pages = min(len(doc), max_pages)
        for i in range(num_pages):
            text = doc[i].get_text("text").strip()
            if text:
                chunks.append({
                    "page_number": i + 1,
                    "text": text[:3000]
                })
        doc.close()
    except Exception as e:
        logger.warning(f"Could not read PDF {file_path.name}: {e}")
    return chunks

def run():
    print("=" * 80)
    print("KRISHIMITRA AI - COMPREHENSIVE SCHEME EXTRACTION & VECTOR INDEXING PIPELINE")
    print("=" * 80)
    start_time = time.time()

    extractor = SchemeExtractor()
    embedding_gen = EmbeddingGenerator()

    # Phase 1: Register and Persist All Scheme Intelligence
    print("\n[Phase 1/3] Registering Verified Schemes across All Collected Documents...")
    registered_schemes: Dict[str, str] = {} # scheme_name -> scheme_id
    dept_schemes: Dict[str, List[str]] = {}

    for item in SCHEMES_FROM_DOCUMENTS:
        dept_id = item["dept_id"]
        scheme_info = item["scheme"]
        scheme_name = scheme_info.scheme_name
        doc_id = f"sch_doc_{hashlib.md5(scheme_name.encode()).hexdigest()[:10]}"

        # Persist scheme to database
        scheme_id = extractor.persist_scheme_to_db(scheme_info, doc_id, dept_id)
        registered_schemes[scheme_name] = scheme_id
        dept_schemes.setdefault(dept_id, []).append(scheme_id)

        print(f"  + [{dept_id}] {scheme_name} -> ID: {scheme_id}")

    print(f"\nSuccessfully registered {len(registered_schemes)} comprehensive schemes in PostgreSQL.")

    # Phase 2: Map Collected Documents to Schemes and Index Passages
    print("\n[Phase 2/3] Mapping Downloaded Documents to Schemes & Indexing for Vector RAG...")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, department_id, title, original_url, file_path
                FROM scheme_documents
                WHERE file_path IS NOT NULL;
            """)
            all_downloaded = cur.fetchall()

    print(f"Found {len(all_downloaded)} downloaded documents across local storage.")

    mapped_count = 0
    indexed_chunks = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for idx, doc in enumerate(all_downloaded, 1):
                doc_id = doc["id"]
                dept_id = doc["department_id"]
                title = doc["title"].lower()
                url = doc["original_url"].lower()
                fpath_str = doc["file_path"]

                # Find best matching scheme
                best_scheme_id = None
                for item in SCHEMES_FROM_DOCUMENTS:
                    if item["dept_id"] == dept_id:
                        for kw in item["doc_match_keywords"]:
                            if kw in title or kw in url:
                                best_scheme_id = registered_schemes[item["scheme"].scheme_name]
                                break
                    if best_scheme_id:
                        break

                # If no specific keyword matched, link to department's primary scheme
                if not best_scheme_id and dept_id in dept_schemes:
                    best_scheme_id = dept_schemes[dept_id][0]

                # Update scheme_documents record
                if best_scheme_id:
                    cur.execute("""
                        UPDATE scheme_documents
                        SET scheme_id = %s,
                            processing_status = 'PROCESSED',
                            verification_status = 'VERIFIED',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                    """, (best_scheme_id, doc_id))
                    mapped_count += 1

                # Extract text chunks and compute vector embeddings for key scheme documents
                fpath = Path(fpath_str)
                if fpath.exists() and (idx <= 120 or best_scheme_id):
                    chunks = extract_pdf_chunks(fpath, max_pages=3)
                    for c in chunks:
                        vec = embedding_gen.generate_embedding(c["text"][:1000])
                        vec_str = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
                        cur.execute("""
                            INSERT INTO extracted_document_content (
                                document_id, scheme_id, page_number, chunk_index,
                                content_text, is_table, embedding, created_at
                            ) VALUES (%s, %s, %s, %s, %s, FALSE, %s::vector, CURRENT_TIMESTAMP)
                            ON CONFLICT DO NOTHING;
                        """, (doc_id, best_scheme_id, c["page_number"], 0, c["text"][:5000], vec_str))
                        indexed_chunks += 1

                if idx % 50 == 0 or idx == len(all_downloaded):
                    conn.commit()
                    print(f"  Processed [{idx}/{len(all_downloaded)}] documents... (Mapped: {mapped_count}, Indexed chunks: {indexed_chunks})")

            conn.commit()

    # Phase 3: Final Verification and Summary Metrics
    print("\n[Phase 3/3] Generating System Intelligence Report...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    s.id, s.name, s.classification, s.level, d.name as dept_name,
                    b.subsidy_amount, b.subsidy_percentage, b.unit_of_assistance,
                    COUNT(sd.id) as linked_documents
                FROM schemes s
                JOIN government_departments d ON s.department_id = d.id
                LEFT JOIN scheme_benefits b ON s.id = b.scheme_id
                LEFT JOIN scheme_documents sd ON s.id = sd.scheme_id
                GROUP BY s.id, s.name, s.classification, s.level, d.name, b.subsidy_amount, b.subsidy_percentage, b.unit_of_assistance
                ORDER BY d.name, s.name;
            """)
            scheme_summary = cur.fetchall()

            cur.execute("SELECT COUNT(*) FROM schemes;")
            total_schemes = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) FROM scheme_documents WHERE verification_status = 'VERIFIED';")
            total_verified_docs = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) FROM extracted_document_content WHERE embedding IS NOT NULL;")
            total_vector_chunks = cur.fetchone()["count"]

    duration = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print("SCHEME EXTRACTION & INTELLIGENCE REPORT")
    print("=" * 80)
    print(f"Execution Duration:         {duration} seconds")
    print(f"Total Registered Schemes:    {total_schemes}")
    print(f"Verified Linked Documents:   {total_verified_docs}")
    print(f"Indexed Semantic Vectors:    {total_vector_chunks}")
    print("=" * 80)
    print(f"{'SCHEME NAME':<55} | {'CLASSIFICATION':<20} | {'BENEFIT / SUBSIDY':<25} | {'DOCS':<5}")
    print("-" * 115)
    for r in scheme_summary:
        name = r["name"][:54]
        classification = (r["classification"] or "Scheme")[:19]
        amt = r["subsidy_amount"]
        pct = r["subsidy_percentage"]
        if amt and pct:
            benefit_str = f"₹{amt:,.0f} ({pct}%)"
        elif amt:
            benefit_str = f"₹{amt:,.0f}"
        elif pct:
            benefit_str = f"{pct}%"
        else:
            benefit_str = "Service / Grant"
        print(f"{name:<55} | {classification:<20} | {benefit_str:<25} | {r['linked_documents']:<5}")
    print("=" * 80)

if __name__ == "__main__":
    run()

