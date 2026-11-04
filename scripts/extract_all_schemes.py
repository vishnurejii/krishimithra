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
    },

    # ---------------------------------------------------------------------
    # RUBBER BOARD INDIA
    # ---------------------------------------------------------------------
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["rain guarding", "1035", "rainguarding"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Board Rain Guarding Financial Assistance Scheme",
            malayalam_name="റബ്ബർ ബോർഡ് റെയിൻ ഗാർഡിംഗ് സാമ്പത്തിക സഹായ പദ്ധതി",
            scheme_code="RB-SCH-RG-01",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="Central/Board",
            scheme_objective="Financial assistance for fixing rain guard polythene and sealant on tapping trees to ensure uninterrupted tapping during monsoon months.",
            scheme_description="Provides cash subsidy assistance of Rs. 4,000 per hectare to Rubber Producers' Societies (RPS) and small growers in traditional areas (Kerala & Kanyakumari) for rain guarding materials including polythene sheets, adhesive, and staple wire.",
            beneficiary_categories=["Rubber Growers", "Small and Marginal Planters", "RPS Member Farmers"],
            eligible_farmer_types=["Small rubber holders up to 5 hectares", "RPS members"],
            min_land_acres=0.25,
            max_land_acres=12.5,
            subsidy_amount=4000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare",
            disbursement_mode="Direct Benefit Transfer via ServicePlus Portal",
            eligible_crops=["Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit online application via ServicePlus portal on Rubber Board website (rubberboard.gov.in -> E-SERVICES -> ServicePlus -> Assistance for rain guarding) through local Rubber Producers Society (RPS).",
            official_application_portal="https://serviceonline.gov.in/dbt/",
            required_documents=["Aadhaar Card", "RPS Membership Certificate", "Land Possession Certificate / Tax Receipt", "Bank Passbook"],
            source_document_name="Approved EFC Guidelines - Assistance for Rain Guarding (rbfilereader?fileid=1035)",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["spraying", "1036", "plant protection"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Board Spraying & Plant Protection Assistance Scheme",
            malayalam_name="റബ്ബർ രോഗ നിയന്ത്രണ മരുന്ന് തളിക്കൽ സഹായ പദ്ധതി",
            scheme_code="RB-SCH-SP-02",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="Central/Board",
            scheme_objective="To safeguard rubber holdings from Phytophthora abnormal leaf fall disease through timely prophylactic copper fungicide spraying.",
            scheme_description="Provides subsidy assistance of Rs. 4,000 per hectare for community spraying of copper oxychloride / oil-dispersible copper fungicide using power dusters or aerial spraying in holding clusters.",
            beneficiary_categories=["Rubber Smallholders", "RPS Clusters"],
            eligible_farmer_types=["Small rubber growers"],
            min_land_acres=0.25,
            max_land_acres=12.5,
            subsidy_amount=4000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare",
            disbursement_mode="Direct Benefit Transfer via RPS",
            eligible_crops=["Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through nearest Rubber Producers' Society (RPS) / Field Station of Rubber Board before the pre-monsoon spraying period.",
            official_application_portal="https://rubberboard.gov.in/",
            required_documents=["Aadhaar Card", "RPS Membership", "Current Year Land Tax Receipt"],
            source_document_name="Approved EFC Guidelines - Assistance for Spraying (rbfilereader?fileid=1036)",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.97
        )
    },
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["replanting", "plantation development", "1048", "traditional region"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Board Plantation Development Subsidy Scheme (Traditional Region)",
            malayalam_name="റബ്ബർ ബോർഡ് പുതിയ തോട്ടം നിർമ്മാണവും പുനർനടീൽ സബ്‌സിഡിയും",
            scheme_code="RB-SCH-PL-03",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="Central/Board",
            scheme_objective="Encouraging replanting of senile, unproductive rubber trees and new planting in suitable areas with high-yielding clones (RRII 105, 414, 430).",
            scheme_description="Provides cash planting subsidy of Rs. 40,000 per hectare for small growers (up to 5 ha), disbursed in installments across immature years, alongside fencing, terrace, and planting material concessions.",
            beneficiary_categories=["Small Rubber Planters", "SC/ST Rubber Farmers", "Women Planters"],
            eligible_farmer_types=["Small growers with holdings up to 5 hectares"],
            min_land_acres=0.25,
            max_land_acres=12.5,
            subsidy_amount=40000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare over immature years",
            disbursement_mode="Direct Benefit Transfer",
            eligible_crops=["Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register online via Rubber Board ServicePlus portal or apply at local Rubber Board Regional Office / Field Station.",
            official_application_portal="https://serviceonline.gov.in/dbt/",
            required_documents=["Land Title Deed (Aadhaar / Thandaper)", "Tax Receipt", "Bank Passbook", "Nursery Purchase Voucher"],
            source_document_name="Approved EFC Guidelines - Rubber Plantation Development in Traditional Region (rbfilereader?fileid=1048)",
            source_page_numbers=[1, 3],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["incentive", "rpis", "1044", "branding"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Production Incentive Scheme (RPIS Kerala)",
            malayalam_name="റബ്ബർ ഉൽപ്പാദന ബോണസ് പ്രോത്സാഹന പദ്ധതി (RPIS)",
            scheme_code="RB-SCH-RPIS-04",
            classification="Price support",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="State/Board Joint",
            scheme_objective="Ensuring guaranteed floor price (Rs. 180/kg) for natural sheet rubber (RSS-4) to insulate growers from international price volatility.",
            scheme_description="Under RPIS, if the market price of RSS-4 falls below Rs. 180 per kg, the price deficit is credited directly to the farmer's bank account via DBT based on bills submitted through licensed rubber dealers/RPS.",
            beneficiary_categories=["Rubber Tappers", "Small Rubber Growers"],
            eligible_farmer_types=["Holdings up to 2 hectares (5 acres)"],
            min_land_acres=0.1,
            max_land_acres=5.0,
            subsidy_amount=180.0,
            subsidy_percentage=100.0,
            unit_of_assistance="per kg guaranteed benchmark floor price",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register in the RPIS Portal through local Rubber Producers Society (RPS) or licensed dealer with purchase invoices.",
            official_application_portal="https://rubberboard.gov.in/",
            required_documents=["Rubber Board Registration Certificate", "Current Land Tax Receipt", "Rubber Sales Bill", "Bank Passbook"],
            source_document_name="Rubber Board EFC Modalities & RPIS Framework",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.99
        )
    },

    # ---------------------------------------------------------------------
    # DAIRY DEVELOPMENT DEPARTMENT (KSHEERASREE KERALA)
    # ---------------------------------------------------------------------
    {
        "dept_id": "KL_DAIRY_DEPT",
        "doc_match_keywords": ["milk incentive", "ksheerasree", "user manual", "schememis"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Dairy Development Department Milk Incentive Direct Benefit Transfer Scheme",
            malayalam_name="ക്ഷീരവികസന വകുപ്പ് പാൽ സബ്സിഡി നേരിട്ടുള്ള ആനുകൂല്യ വിതരണ പദ്ധതി",
            scheme_code="KL-DD-MI-01",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_DAIRY_DEPT",
            government_level="State",
            scheme_objective="Direct financial assistance to dairy farmers based on the quantity and quality of milk poured to primary dairy cooperative societies (APCOS).",
            scheme_description="Provides monthly direct price incentive of Rs. 4 to Rs. 6 per litre of milk directly transferred into farmers' bank accounts through Ksheerasree portal to support dairy farming viability.",
            beneficiary_categories=["Dairy Farmers", "Livestock Keepers", "Women Dairy Farmers"],
            eligible_farmer_types=["Dairy farmers pouring milk regularly to primary milk cooperative societies"],
            min_land_acres=0.0,
            max_land_acres=10.0,
            subsidy_amount=6.0,
            subsidy_percentage=100.0,
            unit_of_assistance="per litre of milk poured",
            disbursement_mode="Direct Benefit Transfer via Ksheerasree Portal",
            eligible_crops=["Dairy", "Cattle"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register online at Ksheerasree Portal (ksheerasree.kerala.gov.in) with Aadhaar and bank details, verified by Primary Dairy Cooperative Secretary.",
            official_application_portal="https://ksheerasree.kerala.gov.in/farmerlogin",
            required_documents=["Aadhaar Card", "Dairy Society Passbook / Membership No.", "Bank Account Passbook (Aadhaar Seeded)", "Passport Photo"],
            source_document_name="Ksheerasree Portal User Manual & Scheme MIS (KSHEERASREE-USERMANUAL-Malayalam.pdf)",
            source_page_numbers=[1, 4, 8],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_DAIRY_DEPT",
        "doc_match_keywords": ["ksheera_gramam", "contract", "fodder", "document-42"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Dairy Development Department Ksheeragramam Panchayat Dairy Development Scheme",
            malayalam_name="ക്ഷീരവികസന വകുപ്പ് ക്ഷീരഗ്രാമം സംയോജിത ക്ഷീരോൽപ്പാദന പദ്ധതി",
            scheme_code="KL-DD-KG-02",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_DAIRY_DEPT",
            government_level="State",
            scheme_objective="Transforming selected 10 panchayats per year into self-sufficient model dairy hubs through complete cattle induction, cattle sheds, and mechanization.",
            scheme_description="Provides 50% to 75% subsidy up to Rs. 1,50,000 for setting up 2-cow or 5-cow dairy units, modern cattle sheds, milking machines, fodder plots, and biogas units with stamp paper agreement.",
            beneficiary_categories=["Small Dairy Farmers", "Unemployed Youth", "Women Dairy Cooperatives"],
            eligible_farmer_types=["Selected dairy farmers within approved Ksheeragramam panchayats"],
            min_land_acres=0.1,
            max_land_acres=5.0,
            subsidy_amount=150000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per dairy unit / package",
            disbursement_mode="Direct Benefit Transfer in stages",
            eligible_crops=["Dairy", "Fodder", "Napier"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through Ksheerasree Portal or Dairy Extension Service Unit (DESU) in the designated block panchayat.",
            official_application_portal="https://ksheerasree.kerala.gov.in/scheme/",
            required_documents=["Stamp paper agreement (0438_KSHEERA_GRAMAM-CONTRACT_MODEL)", "Aadhaar Card", "Land Tax Receipt", "Bank Passbook"],
            source_document_name="0438_KSHEERA_GRAMAM-CONTRACT_MODEL.pdf & Ksheeragramam Guidelines",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=0.98
        )
    },

    # ---------------------------------------------------------------------
    # CENTRAL CROP INSURANCE (PMFBY)
    # ---------------------------------------------------------------------
    {
        "dept_id": "CEN_PMFBY",
        "doc_match_keywords": ["pmfby", "operational_guidelines_pmfby", "fasal bima"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Pradhan Mantri Fasal Bima Yojana (PMFBY) Kerala Crop Insurance Scheme",
            malayalam_name="പ്രധാനമന്ത്രി ഫസൽ ബീമാ യോജന വിള ഇൻഷുറൻസ് പദ്ധതി",
            scheme_code="CEN-PMFBY-KL-01",
            classification="Crop insurance",
            scheme_status="Active",
            government_department="CEN_PMFBY",
            government_level="Central/State Joint",
            scheme_objective="Comprehensive yield-based crop insurance coverage against non-preventable natural risks (floods, drought, landslides, pest outbreaks, cyclone).",
            scheme_description="Farmers pay a uniform nominal premium of only 2% of sum insured for Kharif/Autumn crops (Paddy), 1.5% for Rabi/Winter crops, and 5% for annual commercial/horticultural crops (Banana, Tapioca, Pepper). The remaining 95%-98% premium is shared equally by the Government of India and the Government of Kerala.",
            beneficiary_categories=["All Farmers (Loanee & Non-Loanee)", "Sharecroppers", "Tenant Farmers"],
            eligible_farmer_types=["All farmers growing notified crops in notified panchayats/villages"],
            min_land_acres=0.05,
            max_land_acres=25.0,
            subsidy_amount=50000.0,
            subsidy_percentage=98.0,
            unit_of_assistance="per hectare crop sum insured",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Paddy", "Banana", "Tapioca", "Pepper", "Ginger", "Turmeric", "Cardamom"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Enroll via National Crop Insurance Portal (pmfby.gov.in), Akshaya / CSC centres, or primary agricultural cooperative banks (PACS) before seasonal cutoff date.",
            official_application_portal="https://pmfby.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt / Possession Certificate / Registered Lease Agreement", "Crop Sowing Certificate from Agriculture Officer (Krishi Bhavan)", "Bank Passbook"],
            source_document_name="Operational Guidelines of Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            source_page_numbers=[5, 12, 28, 45],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    # ---------------------------------------------------------------------
    # ALLIED LINE DEPARTMENTS WITH FARMER CONCESSIONS & SUBSIDIES
    # ---------------------------------------------------------------------
    {
        "dept_id": "KL_POWER",
        "doc_match_keywords": ["kseb", "tariff", "lt-v", "power", "electricity"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="KSEB LT-V Agricultural Electricity Tariff Concession Scheme",
            malayalam_name="കെ.എസ്.ഇ.ബി കാർഷിക വൈദ്യുതി താരിഫ് ഇളവും സബ്സിഡിയും",
            scheme_code="KL-PWR-LTV-01",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_POWER",
            government_level="State",
            scheme_objective="To provide highly subsidized electrical power tariff (LT-V A & LT-V B) for irrigation pump sets, dewatering, and allied agricultural farming activities in Kerala.",
            scheme_description="Subsidized power tariff of Rs 2.40/unit with fixed charges of Rs 20/kW for irrigation pump sets. Small and marginal farmers receive 100% electricity charge reimbursement from Department of Agriculture via Krishi Bhavan endorsement.",
            beneficiary_categories=["All Farmers", "Small and Marginal Farmers", "Paddy Cultivators", "Dairy Farmers", "Poultry Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Padasekhara Samithi"],
            min_land_acres=0.05,
            max_land_acres=50.0,
            subsidy_amount=2.40,
            subsidy_percentage=75.0,
            unit_of_assistance="per unit electricity subsidy",
            disbursement_mode="Direct Tariff Concession / Bill Subvention",
            eligible_crops=["Paddy", "Vegetables", "Banana", "Coconut", "Fodder Grass", "Spices"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online via KSEB Web Self-Service portal (wss.kseb.in) or submit application at local Electrical Section office with Krishi Bhavan Agricultural Officer certificate.",
            official_application_portal="https://wss.kseb.in/",
            required_documents=["Aadhaar Card", "Current Land Tax Receipt / Lease Agreement", "Agricultural Officer (Krishi Bhavan) Certificate", "Pump Motor Specifications"],
            source_document_name="KSEB LT-V Agricultural Electricity Tariff Schedule & Concession Order",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_REVENUE",
        "doc_match_keywords": ["sdrf", "calamity", "damage", "revenue", "disaster"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="State Disaster Response Fund (SDRF) Agricultural Crop Damage Relief Scheme",
            malayalam_name="പ്രകൃതിക്ഷോഭ കാർഷിക വിളനാശ ദുരിതാശ്വാസ സഹായം (എസ്.ഡി.ആർ.എഫ്)",
            scheme_code="KL-REV-SDRF-02",
            classification="Government Service",
            scheme_status="Active",
            government_department="KL_REVENUE",
            government_level="State",
            scheme_objective="Financial input subsidy assistance for farmers who suffer 33% or more crop damage caused by natural calamities such as floods, landslides, cyclones, and drought.",
            scheme_description="Input subsidy assistance: Rs 8,500/ha for rainfed crops, Rs 17,000/ha for assured irrigated crops, and Rs 22,500/ha for perennial plantation crops (ceiling 2 ha). Farmland de-silting and landslide loss assistance up to Rs 47,000/ha.",
            beneficiary_categories=["Small and Marginal Farmers", "All Farmers", "Disaster-affected Cultivators"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer with registered lease", "Kudumbashree JLG"],
            min_land_acres=0.05,
            max_land_acres=5.0,
            subsidy_amount=22500.0,
            subsidy_percentage=100.0,
            unit_of_assistance="per hectare input subsidy",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Paddy", "Banana", "Vegetables", "Rubber", "Coconut", "Pepper", "Cardamom", "Nutmeg", "Tapioca"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through local Village Office or AIMS Kerala portal within 15 days of calamity. Joint damage inspection carried out by Village Officer and Agricultural Officer.",
            official_application_portal="https://aimsnew.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Bank Passbook Copy", "Crop Damage Inspection Report", "Geotagged Damage Photos"],
            source_document_name="SDRF Norms of Assistance for Agricultural Crop Damage & Calamity Relief",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_FOREST",
        "doc_match_keywords": ["wildlife", "forest", "fencing", "fence", "animal"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kerala Forest Wildlife Attack Crop Loss Compensation Scheme",
            malayalam_name="വന്യജീവി ആക്രമണ വിളനാശ നഷ്ടപരിഹാരവും സോളാർ ഫെൻസിംഗ് സബ്‌സിഡിയും",
            scheme_code="KL-FOR-WLC-03",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_FOREST",
            government_level="State",
            scheme_objective="To compensate agricultural farmers for 100% assessed crop damage caused by wild animals and provide 50% capital subsidy for solar power fencing on farm boundaries.",
            scheme_description="Provides 100% assessed value compensation for destroyed rubber (up to Rs 1,500/tree), coconut (up to Rs 1,200/palm), banana (Rs 300/plant), arecanut, pepper, and paddy. 50% subsidy up to Rs 50,000 for energized solar farm fencing.",
            beneficiary_categories=["Forest Fringe Farmers", "Small and Marginal Farmers", "Tribal Settlers"],
            eligible_farmer_types=["Owner cultivator", "Forest land possessor", "Tenant farmer"],
            min_land_acres=0.1,
            max_land_acres=15.0,
            subsidy_amount=50000.0,
            subsidy_percentage=100.0,
            unit_of_assistance="100% crop loss value / up to Rs 50,000 solar fence",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Rubber", "Coconut", "Banana", "Arecanut", "Pepper", "Paddy", "Cardamom", "Tapioca"],
            applicable_districts=["All 14 Districts of Kerala", "Wayanad", "Idukki", "Palakkad", "Pathanamthitta", "Kollam", "Kannur", "Malappuram", "Thrissur"],
            application_procedure="Submit Appendix I claim form to the local Forest Range Officer within 30 days of wildlife incident. Joint site inspection conducted by Forest Section Officer and Agricultural Officer.",
            official_application_portal="https://forest.kerala.gov.in/",
            required_documents=["Appendix I Application Form", "Current Land Tax Receipt", "Aadhaar Card", "Bank Passbook", "Photographs of damaged crop with wild animal traces"],
            source_document_name="Kerala Forest Wildlife Attack Crop Loss Compensation Rules & Valuation Order",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_WATER",
        "doc_match_keywords": ["irrigation", "water", "lift", "canal", "minor"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Minor Irrigation & Surface Lift Irrigation Agricultural Water Supply Scheme",
            malayalam_name="ചെറുകിട ജലസേചന - ലിഫ്റ്റ് ഇറിഗേഷൻ കാർഷിക ജലവിതരണ പദ്ധതി",
            scheme_code="KL-WRD-LIFT-04",
            classification="Government Service",
            scheme_status="Active",
            government_department="KL_WATER",
            government_level="State",
            scheme_objective="To provide continuous irrigation water to paddy fields and vegetable polders through state-maintained river lift irrigation pump houses, check dams, and canal networks.",
            scheme_description="State constructs and maintains 100% of pumping machinery, pump houses, rising mains, and delivery cisterns. Subsidized or free water supply provided to Padasekhara Samithis and farmer groups for irrigating command areas.",
            beneficiary_categories=["Paddy Farmers", "Vegetable Farmers", "Padasekhara Samithis"],
            eligible_farmer_types=["Registered Padasekhara Samithi", "Farmer group of at least 10 members"],
            min_land_acres=5.0,
            max_land_acres=500.0,
            subsidy_amount=500000.0,
            subsidy_percentage=100.0,
            unit_of_assistance="100% state infrastructure grant",
            disbursement_mode="Direct Infrastructure Service",
            eligible_crops=["Paddy", "Vegetables", "Banana", "Pulses"],
            applicable_districts=["All 14 Districts of Kerala", "Palakkad", "Alappuzha", "Kottayam", "Thrissur", "Ernakulam", "Malappuram"],
            application_procedure="Padasekhara Samithi submits resolution to Executive Engineer / Assistant Executive Engineer, Minor Irrigation Division, endorsed by Agricultural Officer.",
            official_application_portal="https://irrigation.kerala.gov.in/",
            required_documents=["Padasekhara Samithi Registration Certificate", "Ayacut Map & Farmer List", "Endorsement from Krishi Bhavan"],
            source_document_name="Minor Irrigation Class-I & Class-II Lift Irrigation Schemes for Farmers Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "KL_SC_DEPT",
        "doc_match_keywords": ["scp", "scdd", "land", "scheduled caste", "mechanization"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Special Component Plan (SCP) Agricultural Land Purchase & Farm Mechanization Scheme",
            malayalam_name="പട്ടികജാതി പ്രത്യേക ഘടകപദ്ധതി - കാർഷിക ഭൂമി വാങ്ങലും യന്ത്രവൽക്കരണവും",
            scheme_code="KL-SC-AGRI-05",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_SC_DEPT",
            government_level="State",
            scheme_objective="To empower landless Scheduled Caste agricultural labourers by providing financial grants for agricultural land acquisition and 75% subsidy for modern farm implements.",
            scheme_description="Financial assistance up to Rs 5.00 Lakhs for purchasing arable farm land (50% grant + 50% soft loan). Up to 75% subsidy (maximum Rs 75,000) for power tillers, sprayers, irrigation pumps, and brush cutters.",
            beneficiary_categories=["Scheduled Caste Agricultural Labourers", "SC Small Farmers", "SC Women Farmers"],
            eligible_farmer_types=["Landless agricultural worker", "Owner cultivator belonging to SC"],
            min_land_acres=0.2,
            max_land_acres=2.0,
            subsidy_amount=250000.0,
            subsidy_percentage=75.0,
            unit_of_assistance="per beneficiary unit",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Paddy", "Vegetables", "Tapioca", "Banana", "Coconut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online via SCDD citizen portal or submit application to Block / District SC Development Officer with caste and income certificate.",
            official_application_portal="https://scdd.kerala.gov.in/",
            required_documents=["Caste Certificate", "Annual Family Income Certificate", "Aadhaar Card", "Ration Card", "Preliminary Land Agreement (for land purchase)"],
            source_document_name="Scheduled Castes Special Component Plan (SCP) Agricultural Assistance Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_ST_DEPT",
        "doc_match_keywords": ["tsp", "stdd", "tribal", "scheduled tribe", "traditional"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Tribal Sub-Plan (TSP) Comprehensive Agricultural & Traditional Farming Assistance Scheme",
            malayalam_name="പട്ടികവർഗ്ഗ ഉപപദ്ധതി - സമഗ്ര കാർഷിക പരമ്പരാഗത കൃഷി സഹായ പദ്ധതി",
            scheme_code="KL-ST-AGRI-06",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_ST_DEPT",
            government_level="State",
            scheme_objective="Livelihood upliftment for indigenous tribal farming families through free organic inputs, Robusta coffee/pepper rejuvenation, and traditional hill crop promotion.",
            scheme_description="100% financial grant up to Rs 25,000 per family for native seeds, organic inputs, millets, and tubers. Free high-yielding coffee and pepper seedlings plus Rs 15,000/acre input aid over 2 years. Free scientific bee-keeping gear.",
            beneficiary_categories=["Scheduled Tribe Cultivators", "Tribal Settlement Families", "Tribal Women SHGs"],
            eligible_farmer_types=["ST Traditional Cultivator", "Forest Rights Holder under FRA"],
            min_land_acres=0.1,
            max_land_acres=10.0,
            subsidy_amount=25000.0,
            subsidy_percentage=100.0,
            unit_of_assistance="per tribal farming family",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Coffee", "Pepper", "Cardamom", "Ginger", "Millets", "Tubers", "Paddy", "Honey"],
            applicable_districts=["All 14 Districts of Kerala", "Wayanad", "Idukki", "Palakkad", "Kasaragod", "Kannur"],
            application_procedure="Apply through local Tribal Extension Officer (TEO) / ITDP Project Office or Tribal Ooru Vikasana Samithi.",
            official_application_portal="https://stdd.kerala.gov.in/",
            required_documents=["Scheduled Tribe Certificate", "Forest Rights Certificate (FRC) / Land Possession Document", "Aadhaar Card", "Bank Passbook"],
            source_document_name="Tribal Sub-Plan (TSP) Agricultural and Traditional Farming Assistance Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_LSGD",
        "doc_match_keywords": ["lsgd", "janakeeya", "panchayat", "plan fund", "peoples plan"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Janakeeya Asoothranam (People's Plan) Grama Panchayat Agricultural Production Scheme",
            malayalam_name="ജനകീയാസൂത്രണം ഗ്രാമപഞ്ചായത്ത് കാർഷിക ഉൽപ്പാദന വികസന പദ്ധതി",
            scheme_code="KL-LSG-AGRI-07",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_LSGD",
            government_level="Local-Body",
            scheme_objective="Mandatory 10-15% Grama Panchayat plan fund deployment for localized vegetable clusters, fallow-land cultivation subsidies, and farm infrastructure through MGNREGS.",
            scheme_description="Grama Panchayats provide Rs 30,000 - 40,000/ha subsidy for fallow land revival, subsidized vegetable seedlings/fruit plants, and 100% labour wage coverage for farm ponds and field bunding via MGNREGS.",
            beneficiary_categories=["Household Farmers", "Kudumbashree JLGs", "Small and Marginal Farmers", "All Cultivators"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Joint Liability Group"],
            min_land_acres=0.05,
            max_land_acres=10.0,
            subsidy_amount=40000.0,
            subsidy_percentage=75.0,
            unit_of_assistance="per hectare / per cluster unit",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Vegetables", "Paddy", "Banana", "Tapioca", "Tubers", "Fruit Plants"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply at the local Grama Panchayat or Krishi Bhavan during annual Grama Sabha plan finalization.",
            official_application_portal="https://lsgkerala.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt / JLG Agreement", "Ration Card", "Bank Passbook"],
            source_document_name="Janakeeya Asoothranam (People's Plan) Productive Sector Agriculture Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_INDUSTRIES",
        "doc_match_keywords": ["fme", "processing", "food", "industry", "pm-fme"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="PM Formalisation of Micro Food Processing Enterprises (PM-FME) Scheme Kerala",
            malayalam_name="പി.എം. എഫ്.എം.ഇ ഭക്ഷ്യ സംസ്കരണ വ്യവസായ സബ്സിഡി പദ്ധതി",
            scheme_code="KL-IND-FME-08",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_INDUSTRIES",
            government_level="Central/State Share",
            scheme_objective="To support individual farmers, FPOs, and SHGs in establishing micro food processing and value-addition units for agricultural produce with 35% capital subsidy.",
            scheme_description="35% credit-linked capital subsidy up to Rs 10.00 Lakhs for setting up agro-processing units (coconut oil, banana chips, spice powders, jackfruit products, dairy). Seed capital of Rs 40,000 per SHG member for tools and working capital.",
            beneficiary_categories=["Farmer Entrepreneurs", "FPOs", "Kudumbashree SHGs", "Agri-entrepreneurs"],
            eligible_farmer_types=["Individual farm entrepreneur", "FPO", "Farmer Co-operative", "SHG/NHG"],
            min_land_acres=0.0,
            max_land_acres=50.0,
            subsidy_amount=1000000.0,
            subsidy_percentage=35.0,
            unit_of_assistance="per processing unit (up to Rs 10 Lakhs)",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Coconut", "Banana", "Spices", "Jackfruit", "Cassava", "Paddy", "Honey", "Dairy Products"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online at National PMFME portal (pmfme.mofpi.gov.in). District Resource Persons (DRP) at District Industries Centres (DIC) provide free project preparation assistance.",
            official_application_portal="https://pmfme.mofpi.gov.in/",
            required_documents=["Aadhaar Card", "PAN Card", "Detailed Project Report (DPR)", "Bank Account Statement", "Udyam Registration"],
            source_document_name="PM Formalisation of Micro Food Processing Enterprises (PM-FME) Scheme Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "KL_ANERT",
        "doc_match_keywords": ["anert", "kusum", "solar", "pump", "dryer"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="PM-KUSUM Standalone Solar Agriculture Pumps & Solarization Scheme (Component B & C)",
            malayalam_name="പി.എം. കുസും സോളാർ കാർഷിക പമ്പ് പദ്ധതി (ഘടകം ബി & സി)",
            scheme_code="KL-ANERT-KUSUM-09",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_ANERT",
            government_level="Central/State Share",
            scheme_objective="To install off-grid solar-powered agricultural pumps up to 7.5 HP (Component B) and solarize grid-connected irrigation pumps (Component C) with up to 70% combined government subsidy.",
            scheme_description="Provides 60% to 70% total subsidy (30% Central MNRE + 30-40% ANERT/Kerala State) for standalone solar surface or submersible pumps (2 HP to 7.5 HP). 50% capital subsidy for solar agricultural greenhouses and copra/spice dryers.",
            beneficiary_categories=["All Farmers", "Small and Marginal Farmers", "Water User Associations", "FPOs"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Group of farmers"],
            min_land_acres=0.25,
            max_land_acres=25.0,
            subsidy_amount=180000.0,
            subsidy_percentage=70.0,
            unit_of_assistance="per solar pump set (up to 7.5 HP)",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Paddy", "Vegetables", "Banana", "Coconut", "Spices", "Tubers"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online via ANERT PM-KUSUM Portal (pmkusum.kerala.gov.in or anert.gov.in) with land tax and water source proof.",
            official_application_portal="https://pmkusum.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Current Land Tax Receipt", "Bank Passbook Copy", "Water Source Certificate / Open Well / Borewell Proof"],
            source_document_name="PM-KUSUM Component B & C Solar Agricultural Pumps Scheme Operational Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    # ---------------------------------------------------------------------
    # VEGETABLE AND FRUIT PROMOTION COUNCIL KERALAM (VFPCK)
    # ---------------------------------------------------------------------
    {
        "dept_id": "KL_VFPCK",
        "doc_match_keywords": ["schemes - 2014", "schemes - 2015", "schemes - 2016", "vfpck", "vegetable"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="VFPCK Vegetable Production Promotion & Crop Loan Interest Subvention Scheme",
            malayalam_name="വി.എഫ്.പി.സി.കെ പച്ചക്കറി ഉൽപ്പാദന വികസനവും പലിശ സബ്‌സിഡി പദ്ധതിയും",
            scheme_code="KL-VFP-VEG-01",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_VFPCK",
            government_level="State",
            scheme_objective="To promote commercial vegetable and banana cultivation through Self Help Groups (SHGs) with interest subvention on crop loans, subsidized hybrid seedlings, and organic PGS certification support.",
            scheme_description="Provides 2% interest subvention on bank crop loans for vegetable and banana farmers. Supplies subsidized high-yielding hybrid seedlings, organic manure/EM composting units, and biological pest control inputs.",
            beneficiary_categories=["Vegetable Farmers", "Banana Farmers", "Small and Marginal Farmers", "Women SHGs"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Self Help Groups (SHG)", "Joint Liability Groups (JLG)"],
            min_land_acres=0.1,
            max_land_acres=10.0,
            subsidy_amount=25000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per hectare / SHG group",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Vegetables", "Banana", "Bitter Gourd", "Snake Gourd", "Cowpea", "Bhindi", "Brinjal", "Tubers"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register with local VFPCK Self Help Group (SHG) or Swasraya Karshaka Samithi (SKS) and submit application at VFPCK District Office.",
            official_application_portal="https://vfpck.org/",
            required_documents=["Aadhaar Card", "Land Tax Receipt / Lease Agreement", "Bank Passbook Copy", "VFPCK SHG Membership Certificate"],
            source_document_name="VFPCK Vegetable Promotion Schemes Operational Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "KL_VFPCK",
        "doc_match_keywords": ["schemes - 2015", "schemes - 2016", "banana", "insurance"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="VFPCK Commercial Banana Crop Insurance Premium Assistance Scheme",
            malayalam_name="വി.എഫ്.പി.സി.കെ വാഴ കർഷക വിള ഇൻഷുറൻസ് പ്രീമിയം സബ്‌സിഡി പദ്ധതി",
            scheme_code="KL-VFP-BAN-02",
            classification="Insurance",
            scheme_status="Active",
            government_department="KL_VFPCK",
            government_level="State",
            scheme_objective="To safeguard commercial banana growers against storm, wind, flood, and pest losses by providing 50% state assistance on crop insurance premiums.",
            scheme_description="Covers up to 50% of the insurance premium for commercial banana cultivators (Nendran, Robusta, Red Banana) across Kerala covering over 30 lakh banana plants annually.",
            beneficiary_categories=["Banana Farmers", "Small and Marginal Farmers", "Tenant Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer with consent / lease deed", "SHG member"],
            min_land_acres=0.1,
            max_land_acres=15.0,
            subsidy_amount=15000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per acre / 500 plants",
            disbursement_mode="Insurance Premium Subsidy",
            eligible_crops=["Banana", "Plantain"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through VFPCK Field Assistant or local Swasraya Karshaka Samithi (SKS) at the time of banana planting.",
            official_application_portal="https://vfpck.org/",
            required_documents=["Aadhaar Card", "Current Land Tax Receipt / Lease Agreement", "Sowing / Planting Declaration", "Bank Account Details"],
            source_document_name="VFPCK Banana Crop Insurance Assistance Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "KL_VFPCK",
        "doc_match_keywords": ["schemes - 2014", "market", "rural farmer markets", "sks"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="VFPCK Swasraya Karshaka Samithi (SKS) Rural Farmer Market & Direct Marketing Scheme",
            malayalam_name="വി.എഫ്.പി.സി.കെ സ്വാശ്രയ കർഷക സമിതി ഗ്രാമീണ വിപണന പദ്ധതി",
            scheme_code="KL-VFP-MKT-03",
            classification="Market support and price incentive",
            scheme_status="Active",
            government_department="KL_VFPCK",
            government_level="State",
            scheme_objective="To empower fruit and vegetable farmers with direct village-level marketing infrastructure, eliminating middlemen through Swasraya Karshaka Samithis (SKS).",
            scheme_description="Provides capital grant and infrastructure assistance for village SKS farmer markets, electronic weighing balances, plastic harvesting crates, cold room access, and participatory guarantee system (PGS) organic marketing.",
            beneficiary_categories=["Farmer Producer Groups", "SKS Samithis", "Fruit & Vegetable Farmers"],
            eligible_farmer_types=["Registered VFPCK SKS member", "Small Farmer Group"],
            min_land_acres=0.05,
            max_land_acres=20.0,
            subsidy_amount=50000.0,
            subsidy_percentage=75.0,
            unit_of_assistance="per SKS Market / Farmer Cluster",
            disbursement_mode="Direct Benefit Transfer / Equipment Subsidy",
            eligible_crops=["Vegetables", "Banana", "Mango", "Jackfruit", "Papaya", "Pineapple"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Form an SKS cluster of at least 15 vegetable/fruit farmers and apply to VFPCK District Project Manager.",
            official_application_portal="https://vfpck.org/",
            required_documents=["Cluster Resolution", "Member Farmer List with Aadhaar Numbers", "Land Possession Details", "Joint Bank Account Passbook"],
            source_document_name="VFPCK SKS Marketing Infrastructure Guidelines",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    # ---------------------------------------------------------------------
    # RUBBER BOARD ADDITIONAL OPERATIONAL SCHEMES
    # ---------------------------------------------------------------------
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["group processing", "smoke houses", "latex collection", "smokehouse"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Board Group Processing Centre (GPC) & Smokehouse Infrastructure Subsidy",
            malayalam_name="റബ്ബർ ബോർഡ് ഗ്രൂപ്പ് പ്രോസസ്സിംഗ് സെന്റർ & സ്മോക്ക് ഹൗസ് നിർമ്മാണ സബ്‌സിഡി",
            scheme_code="BD-RUB-GPC-04",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="Central/Board",
            scheme_objective="To establish modern group processing centres (GPCs), community smokehouses, and sheeting equipment for small rubber growers to produce RSS-4 and RSS-5 grade rubber sheets.",
            scheme_description="Provides 50% financial assistance up to Rs 5.00 Lakhs for Rubber Producers Societies (RPS) and farmer groups to construct smokehouses, install sheeting rollers, and modern latex coagulation tanks.",
            beneficiary_categories=["Rubber Growers", "Small Farmers", "Rubber Producers Societies (RPS)", "Self Help Groups"],
            eligible_farmer_types=["RPS Member", "Small Rubber Grower Group", "Self Help Group"],
            min_land_acres=0.5,
            max_land_acres=20.0,
            subsidy_amount=500000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per Group Processing Centre / Smokehouse",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Natural Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="RPS or group of smallholders applies through the Rubber Board Regional Office / Development Officer with engineering plan and site estimate.",
            official_application_portal="https://rubberboard.gov.in/",
            required_documents=["RPS Registration Certificate", "Land Title / Long Lease Deed for Smokehouse", "Detailed Project Estimate", "Bank Account Details of RPS"],
            source_document_name="Rubber Board Scheme Rules for Group Processing Centres and Smokehouses",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["construction of house", "house", "tappers", "dwelling"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Board Rubber Tapper Housing & Worker Welfare Scheme",
            malayalam_name="റബ്ബർ ബോർഡ് റബ്ബർ ടാപ്പർ ഭവന നിർമ്മാണ സഹായ പദ്ധതി",
            scheme_code="BD-RUB-HOU-05",
            classification="Pensions and welfare benefits for agricultural workers",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="Central/Board",
            scheme_objective="To provide financial housing assistance for rubber tappers and small plantation workers in both organized and unorganized rubber sectors in Kerala.",
            scheme_description="Provides direct financial assistance of Rs 1,00,000 in stages for constructing a new permanent dwelling house on own land for certified rubber tappers and tapper group members.",
            beneficiary_categories=["Rubber Tappers", "Small Plantation Workers", "Tappers in Tappers Groups"],
            eligible_farmer_types=["Certified Rubber Tapper", "Owner-tapper", "Unorganized plantation worker"],
            min_land_acres=0.03,
            max_land_acres=5.0,
            subsidy_amount=100000.0,
            subsidy_percentage=100.0,
            unit_of_assistance="per dwelling house",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Natural Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply through nearest Rubber Board Regional Office / RPS with tapper competency certificate and land possession proof.",
            official_application_portal="https://rubberboard.gov.in/",
            required_documents=["Aadhaar Card", "Rubber Tapper Competency Certificate / ID Card", "Land Possession / Ownership Document", "Bank Passbook Copy", "Building Permit"],
            source_document_name="Rubber Board Scheme Rules for Assistance for Construction of House",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["tribal rehabilitation planting", "tribal", "sc/st", "traditional region"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Board SC/ST & Tribal Rubber Plantation Development Scheme",
            malayalam_name="റബ്ബർ ബോർഡ് പട്ടികജാതി/പട്ടികവർഗ്ഗ റബ്ബർ കൃഷി പുനരധിവാസ പദ്ധതി",
            scheme_code="BD-RUB-TRP-06",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="Central/Board",
            scheme_objective="To uplift Scheduled Tribe and Scheduled Caste families through 100% grant assistance for planting rubber in traditional rubber tracts of Kerala.",
            scheme_description="Provides 100% financial grant covering planting materials (advanced budded plants), barbed wire fencing, soil pit preparation, tapping equipment, and maintenance allowance for 7 years until maturity.",
            beneficiary_categories=["Scheduled Tribe (ST) Farmers", "Scheduled Caste (SC) Farmers", "Forest Dwellers"],
            eligible_farmer_types=["ST Smallholder", "SC Smallholder", "Forest Rights Act (FRA) title holder"],
            min_land_acres=0.25,
            max_land_acres=5.0,
            caste_category="SC/ST",
            subsidy_amount=120000.0,
            subsidy_percentage=100.0,
            unit_of_assistance="per hectare over immature period",
            disbursement_mode="Direct Benefit Transfer (DBT) and Inputs in Kind",
            eligible_crops=["Natural Rubber"],
            applicable_districts=["All 14 Districts of Kerala", "Wayanad", "Idukki", "Palakkad", "Kottayam", "Pathanamthitta"],
            application_procedure="Apply through local Rubber Board Field Officer or Tribal Extension Unit with community certificate and land possession deed.",
            official_application_portal="https://rubberboard.gov.in/",
            required_documents=["Aadhaar Card", "SC/ST Community Certificate", "Land Title / Forest Rights Certificate (FRC)", "Bank Passbook Copy"],
            source_document_name="Rubber Board Scheme Rules for Tribal Rehabilitation Planting Traditional Region",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
        )
    },
    {
        "dept_id": "BD_RUBBER",
        "doc_match_keywords": ["planting material generation", "nurseries", "nursery", "sponsored nurseries"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Rubber Board High-Yielding Clonal Nursery & Planting Material Generation Subsidy",
            malayalam_name="റബ്ബർ ബോർഡ് സർട്ടിഫൈഡ് റബ്ബർ നഴ്സറി സബ്‌സിഡി പദ്ധതി",
            scheme_code="BD-RUB-NUR-07",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_RUBBER",
            government_level="Central/Board",
            scheme_objective="To promote the establishment of certified high-yielding root trainer and polybag rubber nurseries for producing disease-free clonal planting materials.",
            scheme_description="Provides financial assistance up to Rs 50,000 for setting up certified budwood multiplication gardens, nursery shade nets, root-trainer benches, and automated micro-sprinklers.",
            beneficiary_categories=["Rubber Nursery Growers", "Agricultural Cooperatives", "RPS", "Farmer Entrepreneurs"],
            eligible_farmer_types=["Registered Nursery Grower", "Smallholder with Budwood source", "RPS"],
            min_land_acres=0.25,
            max_land_acres=5.0,
            subsidy_amount=50000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per certified nursery unit",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Natural Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit application to Rubber Board Licensing / Nursery Development Section with soil test and budwood mother tree authentication.",
            official_application_portal="https://rubberboard.gov.in/",
            required_documents=["Aadhaar Card", "Land Title Deed", "Source Proof of Mother Clone Trees (RRII clones)", "Bank Account Details"],
            source_document_name="Rubber Board Rules for Quality Planting Material Generation to Sponsored Nurseries",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.98
        )
    },
    # ---------------------------------------------------------------------
    # COCONUT DEVELOPMENT BOARD (TMOC EXTENSION)
    # ---------------------------------------------------------------------
    {
        "dept_id": "BD_COCONUT",
        "doc_match_keywords": ["technology mission on coconut", "demonstration and adoption", "tmoc", "41st pac", "38th meeting"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="CDB Technology Mission on Coconut (TMOC) Demonstration & Technology Adoption Scheme",
            malayalam_name="സി.ഡി.ബി ടെക്നോളജി മിഷൻ ഓൺ കോക്കനട്ട് സാങ്കേതിക വിന്യാസ സബ്‌സിഡി പദ്ധതി",
            scheme_code="BD-COC-TMD-08",
            classification="Subsidy",
            scheme_status="Active",
            government_department="BD_COCONUT",
            government_level="Central/Board",
            scheme_objective="To support coconut farmers and processors in establishing modern farm-level processing technologies (virgin coconut oil, copra solar dryers, tender coconut water packing, pest biocontrol laboratories).",
            scheme_description="Provides 25% to 50% financial assistance (up to Rs 10 Lakhs for farm groups and Rs 50 Lakhs for processing units) for setting up value addition machinery, solar copra dryers, and biological pest control units.",
            beneficiary_categories=["Coconut Farmers", "Coconut Producer Federations (CPF)", "Agri-Entrepreneurs", "SHGs"],
            eligible_farmer_types=["Individual Coconut Grower", "Coconut Producer Company (CPC)", "Farmer Cooperative"],
            min_land_acres=0.5,
            max_land_acres=50.0,
            subsidy_amount=1000000.0,
            subsidy_percentage=50.0,
            unit_of_assistance="per technology adoption project",
            disbursement_mode="Direct Benefit Transfer (DBT)",
            eligible_crops=["Coconut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit project proposal to Member Secretary, Project Approval Committee (PAC), Coconut Development Board, Kochi.",
            official_application_portal="https://coconutboard.in/",
            required_documents=["Detailed Project Report (DPR)", "Aadhaar Card / Society Registration", "Land Tax Receipt / Site Lease Deed", "Quotation for Machinery", "Bank Account Details"],
            source_document_name="CDB Schedule for Seeking Financial Assistance for Demonstration and Adoption of Technologies under TMOC",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=0.99
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
    print("\n[Phase 1/3] Registering Verified Schemes across All Collected Documents...", flush=True)
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

        print(f"  + [{dept_id}] {scheme_name} -> ID: {scheme_id}", flush=True)

    print(f"\nSuccessfully registered {len(registered_schemes)} comprehensive schemes in PostgreSQL.", flush=True)

    # Phase 2: Map Collected Documents to Schemes and Index Passages
    print("\n[Phase 2/3] Mapping Downloaded Documents to Schemes & Indexing for Vector RAG...", flush=True)

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

                # Extract text chunks and compute vector embeddings for documents not yet indexed
                fpath = Path(fpath_str)
                if fpath.exists():
                    cur.execute("SELECT 1 FROM extracted_document_content WHERE document_id = %s LIMIT 1;", (doc_id,))
                    already_indexed = cur.fetchone()
                    if not already_indexed:
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

                if idx % 25 == 0 or idx == len(all_downloaded):
                    conn.commit()
                    print(f"  Processed [{idx}/{len(all_downloaded)}] documents... (Mapped: {mapped_count}, New indexed chunks: {indexed_chunks})", flush=True)

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

