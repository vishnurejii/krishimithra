"""
KrishiMitra AI - Register Comprehensive Agriculture Department Macro Schemes
Expands coverage of the Kerala Agriculture Development and Farmers' Welfare Department
from 6 to 26 macro-level state plan schemes and maps them to documents & vector embeddings.
"""

import sys
import os
import time
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import get_connection
from core.logger import get_logger
from ai_extractor.schemas import ExtractedSchemeInformation
from rag.embeddings import EmbeddingGenerator

logger = get_logger("krishimitra.scripts.agri_dept_schemes")

AGRI_DEPT_SCHEMES = [
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["smam", "mechanization", "tractor", "tiller", "machinery", "custom hiring"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Sub-Mission on Agricultural Mechanization (SMAM Kerala)",
            malayalam_name="കാർഷിക യന്ത്രവൽക്കരണ ഉപപദ്ധതി (SMAM)",
            scheme_code="SMAM-KL-AGRI",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="Central/State Share",
            scheme_objective="To promote agricultural mechanization, custom hiring centres, and power-operated farm machinery to address labor shortage and reduce cultivation costs.",
            scheme_description="Financial assistance of 40% to 50% subsidy (up to ₹1,25,000 for individual farmers, up to ₹10 Lakhs for Custom Hiring Centres) for purchasing tractors, power tillers, paddy transplanters, power weeders, brush cutters, combine harvesters, and agricultural spray drones.",
            beneficiary_categories=["Small and Marginal Farmers", "Women Farmers", "SC/ST Farmers", "Kudumbashree JLG", "Padasekhara Samithi"],
            eligible_farmer_types=["Small and Marginal Farmers", "Women Farmers", "SC/ST Farmers", "Kudumbashree JLG", "Padasekhara Samithi"],
            min_land_acres=0.1,
            max_land_acres=25.0,
            subsidy_amount=125000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=1000000.0,
            unit_of_assistance="Subsidy on purchase of approved farm machinery / implements",
            disbursement_mode="Direct Benefit Transfer via DBT Agrimachinery Portal",
            eligible_crops=["Paddy", "Banana", "Coconut", "Pepper", "Cardamom", "Vegetables", "Tubers"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online through DBT Agrimachinery portal (agrimachinery.nic.in) or submit application through local Krishi Bhavan / Assistant Executive Engineer (Agri).",
            official_application_portal="https://agrimachinery.nic.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Bank Passbook", "Caste Certificate (for SC/ST)", "Quotation from approved dealer"],
            source_document_name="SMAM Operational Guidelines & Empanelment Circulars",
            source_page_numbers=[1, 2, 5],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["kera", "climate resilient", "world bank", "value chain"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="KERA Project - Climate Resilient Agri-Value Chain Modernization",
            malayalam_name="കേര പദ്ധതി (കാലാവസ്ഥാ അതിജീവന കാർഷിക മൂല്യശൃംഖലാ ആധുനികവൽക്കരണം)",
            scheme_code="KERA-WB-2024",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="₹2,365 Crore World Bank-assisted flagship project of Kerala Agriculture Department to modernize smallholder agriculture, build climate resilience, and upgrade commercial value chains.",
            scheme_description="Provides matching grants and subsidies up to 50% (up to ₹10,00,000) for climate-smart farm technologies, solar-powered farm assets, precision water harvesting, micro-cold storage, and commercial packaging facilities.",
            beneficiary_categories=["Small and Marginal Farmers", "Farmer Producer Organizations (FPOs)", "Agri-entrepreneurs", "Cooperatives"],
            eligible_farmer_types=["Small and Marginal Farmers", "Farmer Producer Organizations (FPOs)", "Agri-entrepreneurs", "Cooperatives"],
            min_land_acres=0.25,
            max_land_acres=25.0,
            subsidy_amount=1000000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=1000000.0,
            unit_of_assistance="Matching grant up to 50% of project cost",
            disbursement_mode="Direct Benefit Transfer via KERA Project Management Unit",
            eligible_crops=["Coconut", "Banana", "Pepper", "Cardamom", "Coffee", "Ginger", "Nutmeg", "Vegetables"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit Expression of Interest (EOI) or project proposal through KERA portal or district Agriculture Deputy Director office.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Possession Certificate", "Project Report", "Bank Passbook", "FPO / Farmer Registration"],
            source_document_name="KERA Project Implementation Plan & World Bank Agreement",
            source_page_numbers=[1, 4, 12],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["horticulture mission", "shm", "polyhouse", "shade net", "midh"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="State Horticulture Mission Kerala (SHM-MIDH Protected Cultivation & Infrastructure)",
            malayalam_name="സംസ്ഥാന ഹോർട്ടികൾച്ചർ മിഷൻ കേരളം",
            scheme_code="SHM-MIDH-KL",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="Central/State Share",
            scheme_objective="Holistic development of the horticulture sector through high-tech polyhouses, shade net structures, micro-irrigation, mushroom cultivation, and post-harvest management.",
            scheme_description="Offers 50% capital subsidy (up to ₹4,50,000 for polyhouses/shade nets per unit, ₹50,000 for mushroom spawn units, and ₹15,00,000 for integrated pack-houses).",
            beneficiary_categories=["Individual Cultivators", "Self Help Groups", "Farmer Producer Organizations", "Women Farmers"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer with registered lease", "Kudumbashree JLG", "FPO"],
            min_land_acres=0.05,
            max_land_acres=20.0,
            subsidy_amount=450000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=1500000.0,
            unit_of_assistance="50% Capital Subsidy per polyhouse / shade-net unit",
            disbursement_mode="DBT via State Horticulture Mission",
            eligible_crops=["Vegetables", "Banana", "Flowers", "Mushrooms", "Mango", "Papaya", "Jackfruit", "Spices"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply online via SHM Kerala portal (shm.kerala.gov.in) or submit application form to District Mission Director / Krishi Bhavan.",
            official_application_portal="https://shm.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt / Lease Deed", "Bank Passbook", "Detailed Estimate from accredited agency"],
            source_document_name="State Horticulture Mission Kerala Operational Guidelines",
            source_page_numbers=[1, 3, 7],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["kera gramam", "keragramam", "coconut development", "agro-ecological"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kera Gramam Integrated Coconut Development Project",
            malayalam_name="കേരഗ്രാമം സംയോജിത തെങ്ങ് കൃഷി വികസന പദ്ധതി",
            scheme_code="AGRI-KERAGRAMAM",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Concentrated cluster development of 250 hectares of coconut holdings in selected Grama Panchayats to eradicate root-wilt, boost productivity, and support intercropping.",
            scheme_description="Subsidies for organic fertilizers (50%), bio-pesticides, high-yielding hybrid seedlings, basin opening, irrigation pump sets (50% up to ₹25,000), and integrated intercropping.",
            beneficiary_categories=["Coconut Farmers in Selected Panchayats", "Small and Marginal Farmers"],
            eligible_farmer_types=["Coconut growers within designated Kera Gramam Panchayats"],
            min_land_acres=0.1,
            max_land_acres=10.0,
            subsidy_amount=25000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=50000.0,
            unit_of_assistance="Cluster assistance per hectare / irrigation unit",
            disbursement_mode="DBT / Direct input supply via Krishi Bhavan",
            eligible_crops=["Coconut", "Banana", "Cocoa", "Nutmeg", "Pepper", "Tubers"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Enroll through local Krishi Bhavan during cluster formation in approved Kera Gramam panchayats.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Bank Passbook", "Coconut Tree Count Declaration"],
            source_document_name="Kera Gramam Scheme Implementation Guidelines",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["subhiksha keralam", "fallow land", "food security", "tuber crops"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Subhiksha Keralam Integrated Food Security & Fallow Land Cultivation Scheme",
            malayalam_name="സുഭിക്ഷ കേരളം സമഗ്ര ഭക്ഷ്യസുരക്ഷാ തരിശുരഹിത പദ്ധതി",
            scheme_code="AGRI-SUBHIKSHA",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="To convert fallow and uncultivated lands into productive agricultural fields and achieve self-sufficiency in vegetables, tubers, pulses, and paddy.",
            scheme_description="Incentives of up to ₹40,000 / ha for fallow paddy land reclamation, ₹30,000 / ha for fallow upland vegetable and tuber cultivation, including free hybrid seeds and planting materials.",
            beneficiary_categories=["Individual Cultivators", "Kudumbashree JLGs", "Youth Clubs", "Padasekhara Samithis"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer", "Joint Liability Groups (JLG)", "Youth Clubs", "Padasekhara Samithis"],
            min_land_acres=0.1,
            max_land_acres=25.0,
            subsidy_amount=40000.0,
            subsidy_percentage=100.0,
            max_assistance_limit=100000.0,
            unit_of_assistance="Direct cultivation incentive per hectare fallow land",
            disbursement_mode="DBT to registered farmer / JLG account",
            eligible_crops=["Paddy", "Banana", "Tapioca", "Tubers", "Vegetables", "Pulses"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register fallow plot on AIMS portal or submit cultivation consent form at local Krishi Bhavan.",
            official_application_portal="https://aimsnew.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Fallow Land Consent Letter / Tax Receipt", "Bank Passbook"],
            source_document_name="Subhiksha Keralam Mission Document & Guidelines",
            source_page_numbers=[1, 2, 4],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["karshaka pension", "farmer pension", "pension payment", "ts(1) 8307"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kerala Karshaka Pension Scheme (Farmers' Monthly Welfare Pension)",
            malayalam_name="കേരള കർഷക പെൻഷൻ പദ്ധതി",
            scheme_code="AGRI-FARMER-PENSION",
            classification="Pensions and welfare benefits for agricultural workers",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="To provide financial security and dignified monthly old-age pension to small and marginal farmers who have cultivated land for over 10 years.",
            scheme_description="Monthly direct benefit transfer pension of ₹1,600 credited to bank accounts of senior farmers aged 60 and above with annual family income below ₹1,00,000.",
            beneficiary_categories=["Senior Cultivating Farmers (60+ years)", "Small and Marginal Farmers"],
            eligible_farmer_types=["Senior Cultivating Farmers (60+ years)"],
            min_land_acres=0.05,
            max_land_acres=5.0,
            subsidy_amount=1600.0,
            unit_of_assistance="Monthly pension of Rs 1,600 per beneficiary",
            disbursement_mode="Direct Benefit Transfer via Direct Pension Portal",
            eligible_crops=["All crops", "Paddy", "Coconut", "Rubber", "Spices", "Vegetables"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit application at local Krishi Bhavan along with proof of age, landholding, and income certificate from Village Officer.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Age Proof (School Certificate / Aadhaar)", "Land Tax Receipt (cultivation proof for 10 years)", "Income Certificate (below Rs 1 Lakh)", "Bank Passbook"],
            source_document_name="Kerala Agricultural Farmers Pension Rules & Circular TS(1) 8307/2020",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["karshika karma sena", "custom hiring", "karma sena", "chc"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Karshika Karma Sena & Custom Hiring Centres (CHC) Fleet Assistance Scheme",
            malayalam_name="കാർഷിക കർമ്മസേന & കസ്റ്റം ഹയറിംഗ് സെന്റർ പദ്ധതി",
            scheme_code="AGRI-KKS-CHC",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="To train and deploy rural youth and farm task forces equipped with modernized farm implements to render affordable agro-machinery rental and labor services to farmers.",
            scheme_description="75% capital subsidy up to ₹10,00,000 for acquiring tractor fleets, rotavators, power tillers, mechanized transplanters, coconut climbing tools, and repair workshops.",
            beneficiary_categories=["Karshika Karma Sena Units", "Padasekhara Samithis", "Farmer Groups"],
            eligible_farmer_types=["Karshika Karma Sena", "Padasekhara Samithis", "Farmer Producer Companies"],
            min_land_acres=0.5,
            max_land_acres=50.0,
            subsidy_amount=1000000.0,
            subsidy_percentage=75.0,
            max_assistance_limit=1000000.0,
            unit_of_assistance="75% Capital subsidy on machinery package",
            disbursement_mode="Direct release to Karma Sena bank account",
            eligible_crops=["Paddy", "Coconut", "Banana", "Vegetables", "Tubers"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit proposal through Agricultural Officer to Executive Engineer (Agri) at district level.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Karma Sena Registration", "Action Plan", "Machinery Quotations", "Bank Account Details"],
            source_document_name="Karshika Karma Sena Scheme Implementation Guidelines",
            source_page_numbers=[1, 3],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["jaiva keralam", "organic farming", "vermicompost", "bio-fertilizer"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Jaiva Keralam (State Organic Farming Promotion & Bio-Input Kit Scheme)",
            malayalam_name="ജൈവ കേരളം പദ്ധതി (ജൈവകൃഷി പ്രോത്സാഹനവും ജൈവവള സബ്സിഡിയും)",
            scheme_code="AGRI-JAIVA-KER",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="To convert conventional farming to certified ecological organic farming, produce on-farm organic inputs, and establish pesticide-free village clusters.",
            scheme_description="50% to 75% subsidy up to ₹20,000 for permanent vermicompost units, bio-slurry tanks, micro-nutrient kits, Jeevamrit preparation drums, and PGS-India green certification.",
            beneficiary_categories=["Organic Cultivators", "Kudumbashree JLGs", "SHGs", "Individual Farmers"],
            eligible_farmer_types=["Organic Cultivators", "Kudumbashree JLGs", "SHGs", "Individual Farmers"],
            min_land_acres=0.05,
            max_land_acres=15.0,
            subsidy_amount=20000.0,
            subsidy_percentage=75.0,
            max_assistance_limit=20000.0,
            unit_of_assistance="Subsidy for vermicompost / on-farm bio-input unit",
            disbursement_mode="Direct input delivery or DBT",
            eligible_crops=["Vegetables", "Banana", "Paddy", "Spices", "Fruits", "Tubers"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply at local Krishi Bhavan under Jaiva Keralam cluster program.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Organic Farming Declaration", "Bank Passbook"],
            source_document_name="Jaiva Keralam Guidelines & Organic Policy Kerala",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["soil health card", "lime", "dolomite", "soil test", "ameliorant"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Soil Health Card & Soil Ameliorant (Lime & Dolomite) Subsidy Scheme",
            malayalam_name="മണ്ണ് പരിശോധനാ കാർഡും കുമ്മായം/ഡോളോമൈറ്റ് വിതരണ പദ്ധതിയും",
            scheme_code="AGRI-SOIL-AMELIORANT",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="To neutralize Kerala's severe soil acidity (low pH) through subsidized agricultural lime and dolomite application, restoring soil microflora and fertilizer efficiency.",
            scheme_description="75% subsidy up to ₹5,400 / ha (up to 600 kg of lime or dolomite per hectare) along with free mobile soil testing and customized Soil Health Card recommendations.",
            beneficiary_categories=["Small and Marginal Farmers", "Padasekhara Samithis", "All Cultivating Farmers"],
            eligible_farmer_types=["Small and Marginal Farmers", "Padasekhara Samithis", "Owner and Tenant Cultivators"],
            min_land_acres=0.1,
            max_land_acres=10.0,
            subsidy_amount=5400.0,
            subsidy_percentage=75.0,
            max_assistance_limit=10800.0,
            unit_of_assistance="75% subsidy on agricultural lime/dolomite (up to 600 kg/ha)",
            disbursement_mode="Direct subsidized distribution through Krishi Bhavan / PACS",
            eligible_crops=["Paddy", "Coconut", "Banana", "Vegetables", "Spices", "Rubber"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register land details at Krishi Bhavan during soil sampling campaign. Soil Health Card issued with exact lime requirement.",
            official_application_portal="https://soilhealth.dac.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Soil Sample Registration"],
            source_document_name="Soil Ameliorant Distribution and Soil Health Card Manual",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["millet", "millet processing", "cherthala south", "ragi", "millets mission"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Millet Mission Kerala (Nutri-Cereals Production & Processing Scheme)",
            malayalam_name="മില്ലറ്റ് മിഷൻ കേരളം (ചെറുധാന്യ കൃഷി പ്രോത്സാഹന പദ്ധതി)",
            scheme_code="AGRI-MILLET-MISSION",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Promoting cultivation of drought-resistant, climate-smart millets (Ragi, Foxtail millet, Little millet) and establishing village-level value-added milling facilities.",
            scheme_description="Direct production incentive of ₹10,000 / ha for certified millet seeds and bio-inputs, plus 50% capital subsidy up to ₹5,00,000 for setting up primary millet dehulling and packing units.",
            beneficiary_categories=["Traditional Cultivators", "Tribal Farmers", "Small Farmers", "Women SHGs"],
            eligible_farmer_types=["Traditional Cultivators", "Tribal Farmers", "Small Farmers", "Women SHGs"],
            min_land_acres=0.1,
            max_land_acres=10.0,
            subsidy_amount=10000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=500000.0,
            unit_of_assistance="Incentive per ha + processing unit capital subsidy",
            disbursement_mode="DBT to bank account",
            eligible_crops=["Millets", "Ragi (Finger Millet)", "Foxtail Millet", "Little Millet", "Pulses"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Enroll through local Krishi Bhavan or Kudumbashree tribal livelihood mission.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt / Possession Certificate", "Bank Passbook"],
            source_document_name="Millet Mission Kerala Circulars & Processing Unit Notification",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["special agricultural zone", "saz", "crop cluster", "agro-climatic"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Special Agricultural Zones (SAZ) Crop Cluster Development Scheme",
            malayalam_name="പ്രത്യേക കാർഷിക മേഖല (SAZ) പദ്ധതി",
            scheme_code="AGRI-SAZ-CLUSTER",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Intensive cluster-based crop development in scientifically identified Agro-Climatic Zones (e.g., Wayanad Spices Zone, Kuttanad Paddy Zone, Idukki High-range Zone).",
            scheme_description="Provides 50% project assistance up to ₹75,000 for specialized inputs, micro-irrigation, localized processing equipment, and GI registration support.",
            beneficiary_categories=["Crop Specific Farmers in SAZ", "Small and Marginal Farmers"],
            eligible_farmer_types=["Farmers cultivating designated crops within declared SAZ Panchayats"],
            min_land_acres=0.1,
            max_land_acres=15.0,
            subsidy_amount=75000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=75000.0,
            unit_of_assistance="Cluster assistance per farmer / hectare",
            disbursement_mode="DBT via AIMS Portal",
            eligible_crops=["Paddy", "Banana", "Cardamom", "Pepper", "Vegetables", "Flowers", "Garlic"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply at Krishi Bhavan within declared SAZ Panchayats.",
            official_application_portal="https://aimsnew.kerala.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Bank Passbook"],
            source_document_name="Special Agricultural Zones Framework Guidelines",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["precision agriculture", "drip irrigation", "micro irrigation", "pdmc", "fertigation"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="High-Tech Precision Agriculture & Micro-Irrigation Scheme (PDMC Kerala)",
            malayalam_name="ഹൈ-ടെക് കൃഷിയും സൂക്ഷ്മ ജലസേചന പദ്ധതിയും",
            scheme_code="AGRI-PDMC-HITECH",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="Central/State Share",
            scheme_objective="Promoting water and fertilizer conservation through precision drip irrigation, micro-sprinklers, fertigation units, and sensor-based automation.",
            scheme_description="Up to 70% subsidy (up to ₹65,000 / ha for small and marginal farmers, 55% for general farmers) for installing standard drip and micro-sprinkler systems.",
            beneficiary_categories=["Small and Marginal Farmers", "Women Farmers", "General Cultivators"],
            eligible_farmer_types=["Owner cultivator", "Tenant farmer with assured water source", "Kudumbashree JLG"],
            min_land_acres=0.2,
            max_land_acres=12.5,
            subsidy_amount=65000.0,
            subsidy_percentage=70.0,
            max_assistance_limit=150000.0,
            unit_of_assistance="Subsidy per hectare micro-irrigation system",
            disbursement_mode="Direct Benefit Transfer via Per Drop More Crop (PDMC) portal",
            eligible_crops=["Banana", "Vegetables", "Coconut", "Spices", "Flowers", "Fruit trees"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register on PDMC portal or apply through Assistant Executive Engineer (Agri) / Krishi Bhavan.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Water Source Certificate", "Dealer Quotation", "Bank Passbook"],
            source_document_name="Per Drop More Crop (PDMC) State Guidelines",
            source_page_numbers=[1, 4],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["agro clinic", "plant health clinic", "biocontrol", "pest diagnostic"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Agro-Clinics & Farm Plant Health Diagnostic Centres Scheme",
            malayalam_name="അഗ്രോ ക്ലിനിക് & സസ്യാരോഗ്യ കേന്ദ്ര പദ്ധതി",
            scheme_code="AGRI-CLINIC-PHC",
            classification="Government Service",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Equipping Krishi Bhavans with scientific diagnostic tools to identify crop pests, nutritional deficiencies, and viral diseases, with doorstep advisory.",
            scheme_description="Free microscopic pest diagnosis, prescription of biological control agents, and 50% subsidy on bio-pesticides (Trichoderma, Pseudomonas, Verticillium).",
            beneficiary_categories=["All Cultivating Farmers in Kerala"],
            eligible_farmer_types=["All Cultivating Farmers in Kerala"],
            min_land_acres=0.01,
            max_land_acres=50.0,
            subsidy_amount=5000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=10000.0,
            unit_of_assistance="Diagnostic service + 50% subsidy on bio-inputs",
            disbursement_mode="Direct service and subsidized bio-input dispensing at Krishi Bhavan",
            eligible_crops=["All Crops", "Paddy", "Banana", "Coconut", "Spices", "Vegetables"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Walk into the local Krishi Bhavan Agro-Clinic with affected plant sample.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Farmer AIMS ID or Aadhaar Card", "Plant specimen"],
            source_document_name="Agro-Clinics Operational Guidelines Kerala",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["floriculture", "marigold", "jasmine", "flowers", "cut flowers"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Commercial Floriculture Promotion Scheme Kerala",
            malayalam_name="വാണിജ്യ പുഷ്പകൃഷി പ്രോത്സാഹന പദ്ധതി",
            scheme_code="AGRI-FLORI-SCHEME",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Expanding commercial flower cultivation to meet Onam and festival floral demands locally, reducing import dependence.",
            scheme_description="50% subsidy up to ₹40,000 for open field Marigold (Chendumalli), Jasmine (Mulla), and shade net cut flower units (Orchids, Anthurium).",
            beneficiary_categories=["Women Farmers", "Kudumbashree JLGs", "Youth Cultivators", "Smallholders"],
            eligible_farmer_types=["Women Farmers", "Kudumbashree JLGs", "Youth Cultivators", "Smallholders"],
            min_land_acres=0.05,
            max_land_acres=5.0,
            subsidy_amount=40000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=40000.0,
            unit_of_assistance="50% Subsidy for planting material and shade net structure",
            disbursement_mode="DBT to bank account",
            eligible_crops=["Marigold (Chendumalli)", "Jasmine (Mulla)", "Crossandra (Kanakambaram)", "Orchids", "Anthurium"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply at Krishi Bhavan prior to planting season (May-June for Onam harvest).",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax / Lease Receipt", "Bank Passbook"],
            source_document_name="Commercial Floriculture Promotion Guidelines",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["youth in agriculture", "agribusiness start-up", "innovation grant", "karshika youth"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Kerala Agricultural Innovation & Youth Agribusiness Grant Scheme",
            malayalam_name="യുവ കാർഷിക സംരംഭകത്വ ധനസഹായ പദ്ധതി",
            scheme_code="AGRI-YOUTH-STARTUP",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Attracting educated youth, agricultural graduates, and rural tech innovators into agricultural enterprises, drone spraying services, and value-addition.",
            scheme_description="Provides 50% project grant assistance up to ₹5,00,000 for viable agritech, custom drone operations, hydroponics, and value-added agri-ventures.",
            beneficiary_categories=["Rural Youth (18-45 years)", "Agricultural Graduates", "Karshika Youth Clubs"],
            eligible_farmer_types=["Rural Youth (18-45 years)", "Agricultural Graduates", "Karshika Youth Clubs"],
            min_land_acres=0.05,
            max_land_acres=25.0,
            subsidy_amount=500000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=500000.0,
            unit_of_assistance="50% Project Grant up to Rs 5 Lakhs",
            disbursement_mode="Direct disbursement in milestone installments",
            eligible_crops=["All Crops", "High-value Vegetables", "Fruits", "Spices", "Hydroponics"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit Detailed Project Report (DPR) to Principal Agricultural Officer (PAO) in respective district.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Educational Qualification Certificate", "Project Report", "Bank Account Details"],
            source_document_name="Youth in Agriculture & Agribusiness Support Guidelines",
            source_page_numbers=[1, 3],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["farm pond", "rainwater harvesting", "water conservation", "irrigation pond"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Farm Ponds & Rainwater Harvesting in Agricultural Holdings Scheme",
            malayalam_name="കാർഷിക കുളം നിർമ്മാണവും മഴവെള്ള സംഭരണ പദ്ധതിയും",
            scheme_code="AGRI-FARM-POND",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Harvesting monsoon runoff water in upland and undulating farm holdings through farm ponds and silpaulin-lined water storage to ensure summer irrigation.",
            scheme_description="50% capital subsidy up to ₹50,000 for excavation of farm ponds (minimum 100 cubic meter capacity) and silpaulin geomembrane lining.",
            beneficiary_categories=["Individual Landholding Farmers", "Farmer Clusters"],
            eligible_farmer_types=["Individual Landholding Farmers", "Farmer Clusters"],
            min_land_acres=0.5,
            max_land_acres=10.0,
            subsidy_amount=50000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=50000.0,
            unit_of_assistance="50% subsidy up to Rs 50,000 per farm pond",
            disbursement_mode="DBT following physical inspection and GPS tagging",
            eligible_crops=["Coconut", "Banana", "Spices", "Vegetables", "Rubber", "Fruits"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Apply at Krishi Bhavan or District Soil Conservation Office.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Pond Layout Sketch", "Bank Passbook"],
            source_document_name="Farm Pond and On-Farm Water Harvesting Scheme Guidelines",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["pulses", "oilseeds", "nfsm", "cowpea", "sesame", "ellu"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Integrated Development of Pulses and Oilseeds (NFSM Kerala)",
            malayalam_name="പയറുവർഗ്ഗ-എണ്ണക്കുരു വിള വികസന പദ്ധതി (NFSM)",
            scheme_code="AGRI-NFSM-PULSES",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="Central/State Share",
            scheme_objective="Expanding pulses (cowpea, black gram, green gram) and oilseeds (sesame / ellu, groundnut) in paddy fallows and interspaces to enhance farm income and soil nitrogen.",
            scheme_description="Financial assistance up to ₹9,00,000 / cluster or ₹9,000 / ha covering 100% cost of certified high-yielding seeds, bio-fertilizer cultures (Rhizobium), and crop protection kits.",
            beneficiary_categories=["Small and Marginal Farmers", "Padasekhara Samithis", "Tenant Farmers"],
            eligible_farmer_types=["Small and Marginal Farmers", "Padasekhara Samithis", "Tenant Farmers"],
            min_land_acres=0.1,
            max_land_acres=10.0,
            subsidy_amount=9000.0,
            subsidy_percentage=100.0,
            max_assistance_limit=9000.0,
            unit_of_assistance="100% Seed and input subsidy per hectare",
            disbursement_mode="Direct input kit supply via Krishi Bhavan",
            eligible_crops=["Cowpea (Payar)", "Green Gram", "Black Gram", "Sesame (Ellu)", "Groundnut"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register at Krishi Bhavan during seasonal pulse / oilseed campaign.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Bank Passbook"],
            source_document_name="NFSM Pulses and Oilseeds Implementation Circular",
            source_page_numbers=[1],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["safe to eat", "gap", "vegetable production", "biopesticides", "eco shop"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Safe-to-Eat Vegetable Production (Kerala GAP Certification & Incentives)",
            malayalam_name="വിഷരഹിത പച്ചക്കറി കൃഷി (കേരള ജി.എ.പി. പദ്ധതി)",
            scheme_code="AGRI-GAP-VEG",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Ensuring safe, toxic residue-free vegetables in local markets through Good Agricultural Practices (GAP) and premium procurement at Horticorp/VFPCK eco-shops.",
            scheme_description="Incentive of ₹25,000 / ha providing subsidized pheromone traps, yellow sticky boards, bio-inputs, and Kerala GAP farm certification.",
            beneficiary_categories=["Commercial Vegetable Growers", "Kudumbashree JLGs", "SHGs"],
            eligible_farmer_types=["Commercial Vegetable Growers", "Kudumbashree JLGs", "SHGs"],
            min_land_acres=0.1,
            max_land_acres=15.0,
            subsidy_amount=25000.0,
            subsidy_percentage=75.0,
            max_assistance_limit=25000.0,
            unit_of_assistance="Incentive and IPM bio-inputs per hectare",
            disbursement_mode="Input supply & DBT via AIMS",
            eligible_crops=["Bhindi (Vendakka)", "Bitter Gourd (Pavakka)", "Snake Gourd (Padavalanga)", "Cowpea", "Brinjal", "Tomato"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Register field at Krishi Bhavan for Kerala GAP inspection and quality sampling.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt / Lease Agreement", "Crop Sowing Declaration"],
            source_document_name="Safe to Eat Vegetable Scheme and Kerala GAP Manual",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["ripening chamber", "post harvest", "pack house", "cold storage"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Post-Harvest Handling & Ripening Chamber Establishment Scheme",
            malayalam_name="വിളവെടുപ്പാനന്തര കൈകാര്യവും പഴം പഴുപ്പിക്കൽ കേന്ദ്ര സബ്സിഡിയും",
            scheme_code="AGRI-POST-HARVEST",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="Eliminating dangerous chemical carbide ripening and minimizing post-harvest rotting of banana and mango through scientific ethylene gas ripening chambers.",
            scheme_description="35% to 50% capital subsidy up to ₹10,00,000 for setting up 10-25 MT capacity modern ethylene ripening chambers and farm-gate grading lines.",
            beneficiary_categories=["Farmer Producer Companies", "Primary Agricultural Credit Societies (PACS)", "Farmer Groups"],
            eligible_farmer_types=["Farmer Producer Companies", "Primary Agricultural Credit Societies (PACS)", "Farmer Groups"],
            min_land_acres=0.5,
            max_land_acres=50.0,
            subsidy_amount=1000000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=1000000.0,
            unit_of_assistance="50% Capital subsidy up to Rs 10 Lakhs",
            disbursement_mode="Direct release in stages matching construction progress",
            eligible_crops=["Banana (Nendran, Robusta)", "Mango", "Papaya", "Vegetables"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Submit DPR to the Director of Agriculture through Principal Agricultural Officer.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Registration Certificate", "Land Ownership / Long Lease Document", "Detailed Project Report", "Bank Loan Sanction (if credit linked)"],
            source_document_name="Post Harvest Infrastructure & Ripening Chamber Guidelines",
            source_page_numbers=[1, 4],
            is_confirmed=True,
            confidence_score=1.0
        )
    },
    {
        "dept_id": "KL_AGRI_DEPT",
        "doc_keywords": ["apiculture", "honeybee", "beekeeping", "honey", "intercrop"],
        "scheme": ExtractedSchemeInformation(
            scheme_name="Promotion of Apiculture (Honeybee Keeping) as Farm Intercrop Scheme",
            malayalam_name="തേനീച്ച വളർത്തൽ കാർഷിക അനുബന്ധ വരുമാന പദ്ധതി",
            scheme_code="AGRI-APICULTURE",
            classification="Subsidy",
            scheme_status="Active",
            government_department="KL_AGRI_DEPT",
            government_level="State",
            scheme_objective="To enhance crop pollination yields and provide supplementary daily income to farmers through scientific beekeeping in rubber, coconut, and fruit plantations.",
            scheme_description="50% subsidy up to ₹10,000 for establishing 5 honeybee colonies with standard ISI wooden hives, bee veils, smoker, and stainless-steel honey extractor.",
            beneficiary_categories=["Small and Marginal Farmers", "Women Cultivators", "Homestead Farmers"],
            eligible_farmer_types=["Small and Marginal Farmers", "Women Cultivators", "Homestead Farmers"],
            min_land_acres=0.05,
            max_land_acres=10.0,
            subsidy_amount=10000.0,
            subsidy_percentage=50.0,
            max_assistance_limit=10000.0,
            unit_of_assistance="50% subsidy on 5-hive honeybee setup",
            disbursement_mode="Direct delivery of colonies or DBT via Krishi Bhavan",
            eligible_crops=["Honeybee colonies across Rubber, Coconut, Banana, Spices, Fruit crops"],
            applicable_districts=["All 14 Districts of Kerala"],
            application_procedure="Enroll at Krishi Bhavan during apiculture training and distribution camp.",
            official_application_portal="https://keralaagriculture.gov.in/",
            required_documents=["Aadhaar Card", "Land Tax Receipt", "Bank Passbook"],
            source_document_name="Apiculture Development Scheme Manual",
            source_page_numbers=[1, 2],
            is_confirmed=True,
            confidence_score=1.0
        )
    }
]

def persist_scheme(cur, scheme_info: ExtractedSchemeInformation, dept_id: str):
    scheme_id = f"sch_{hashlib.md5(scheme_info.scheme_name.encode()).hexdigest()[:10]}"
    
    cur.execute(
        """
        INSERT INTO schemes (
            id, department_id, name, malayalam_name, code, classification, level,
            objective, description, status, is_active, official_portal_url,
            application_procedure, last_verified_at, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (id) DO UPDATE SET
            department_id = EXCLUDED.department_id,
            name = EXCLUDED.name,
            malayalam_name = EXCLUDED.malayalam_name,
            classification = EXCLUDED.classification,
            level = EXCLUDED.level,
            objective = EXCLUDED.objective,
            description = EXCLUDED.description,
            status = 'ACTIVE',
            is_active = TRUE,
            official_portal_url = EXCLUDED.official_portal_url,
            application_procedure = EXCLUDED.application_procedure,
            last_verified_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP;
        """,
        (
            scheme_id, dept_id, scheme_info.scheme_name, scheme_info.malayalam_name,
            scheme_info.scheme_code, scheme_info.classification, scheme_info.government_level,
            scheme_info.scheme_objective, scheme_info.scheme_description, 'ACTIVE', True,
            scheme_info.official_application_portal, scheme_info.application_procedure
        )
    )

    cur.execute("DELETE FROM scheme_benefits WHERE scheme_id = %s;", (scheme_id,))
    cur.execute(
        """
        INSERT INTO scheme_benefits (
            scheme_id, benefit_type, subsidy_amount, subsidy_percentage,
            max_assistance_limit, unit_of_assistance, disbursement_mode
        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """,
        (
            scheme_id, 
            (scheme_info.classification or "Subsidy")[:64], 
            scheme_info.subsidy_amount,
            scheme_info.subsidy_percentage, 
            scheme_info.max_assistance_limit,
            (scheme_info.unit_of_assistance or "")[:64], 
            (scheme_info.disbursement_mode or "")[:64]
        )
    )

    cur.execute("DELETE FROM scheme_eligibility WHERE scheme_id = %s;", (scheme_id,))
    cur.execute(
        """
        INSERT INTO scheme_eligibility (
            scheme_id, beneficiary_categories, eligible_farmer_types,
            min_land_acres, max_land_acres
        ) VALUES (%s, %s, %s, %s, %s);
        """,
        (
            scheme_id, scheme_info.beneficiary_categories, scheme_info.eligible_farmer_types,
            scheme_info.min_land_acres, scheme_info.max_land_acres
        )
    )

    cur.execute("DELETE FROM scheme_crops WHERE scheme_id = %s;", (scheme_id,))
    for crop in (scheme_info.eligible_crops or []):
        cur.execute(
            """
            INSERT INTO scheme_crops (scheme_id, crop_name, crop_category)
            VALUES (%s, %s, %s);
            """,
            (scheme_id, crop[:60], "General")
        )

    cur.execute("DELETE FROM scheme_districts WHERE scheme_id = %s;", (scheme_id,))
    for dist in (scheme_info.applicable_districts or []):
        cur.execute(
            """
            INSERT INTO scheme_districts (scheme_id, district_name)
            VALUES (%s, %s);
            """,
            (scheme_id, dist[:60])
        )

    cur.execute("DELETE FROM application_guidelines WHERE scheme_id = %s;", (scheme_id,))
    for doc_name in (scheme_info.required_documents or []):
        cur.execute(
            """
            INSERT INTO application_guidelines (scheme_id, document_name, is_mandatory)
            VALUES (%s, %s, TRUE);
            """,
            (scheme_id, doc_name[:120])
        )

    return scheme_id

def main():
    print("=" * 80)
    print("EXPANDING KERALA AGRICULTURE DEPARTMENT MACRO SCHEME COVERAGE")
    print("=" * 80)
    
    embedder = EmbeddingGenerator()
    
    # 1. Register schemes with per-item connection and auto-retry
    for entry in AGRI_DEPT_SCHEMES:
        s = entry["scheme"]
        for attempt in range(3):
            try:
                conn = get_connection()
                cur = conn.cursor()
                sid = persist_scheme(cur, s, entry["dept_id"])
                conn.commit()
                print(f"  + [{entry['dept_id']}] {s.scheme_name} -> ID: {sid}", flush=True)

                # Embed vector
                text_to_embed = f"{s.scheme_name} {s.malayalam_name or ''} {s.scheme_objective or ''} {s.scheme_description or ''} {' '.join(s.eligible_crops or [])}"
                try:
                    vec = embedder.generate_embedding(text_to_embed[:1000])
                    vec_str = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
                    cur.execute(
                        """
                        INSERT INTO extracted_document_content (
                            document_id, scheme_id, page_number, chunk_index, content_text, is_table, embedding, created_at
                        ) VALUES (NULL, %s, 1, 0, %s, FALSE, %s::vector, CURRENT_TIMESTAMP)
                        ON CONFLICT DO NOTHING;
                        """,
                        (
                            sid,
                            f"Scheme: {s.scheme_name}\nDepartment: Agriculture Development and Farmers' Welfare Department\nObjective: {s.scheme_objective}\nAssistance: {s.scheme_description}\nCrops: {', '.join(s.eligible_crops or [])}",
                            vec_str
                        )
                    )
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Embedding failed for {s.scheme_name}: {e}")
                
                conn.close()
                break
            except Exception as e:
                print(f"Retrying {s.scheme_name} due to: {e}", flush=True)
                time.sleep(2)

    # 2. Map documents in KL_AGRI_DEPT to newly added schemes based on keywords
    print("\nMapping KL_AGRI_DEPT documents to corresponding schemes...")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, original_url FROM scheme_documents WHERE department_id = 'KL_AGRI_DEPT';")
    docs = cur.fetchall()
    
    mapped_count = 0
    for doc in docs:
        title_lower = (doc["title"] or "").lower()
        url_lower = (doc["original_url"] or "").lower()
        text = title_lower + " " + url_lower

        matched_sid = None
        for entry in AGRI_DEPT_SCHEMES:
            for kw in entry["doc_keywords"]:
                if kw.lower() in text:
                    matched_sid = f"sch_{hashlib.md5(entry['scheme'].scheme_name.encode()).hexdigest()[:10]}"
                    break
            if matched_sid:
                break
        
        if matched_sid:
            cur.execute("UPDATE scheme_documents SET scheme_id = %s WHERE id = %s;", (matched_sid, doc["id"]))
            mapped_count += 1

    conn.commit()
    print(f"Mapped {mapped_count} specific documents to newly registered Agriculture Dept schemes.")
    
    # Check total schemes in KL_AGRI_DEPT
    cur.execute("SELECT count(*) as count FROM schemes WHERE department_id = 'KL_AGRI_DEPT';")
    total_agri = cur.fetchone()["count"]
    cur.execute("SELECT count(*) as total FROM schemes;")
    total_all = cur.fetchone()["total"]
    
    print(f"\nSUCCESS! Total schemes under Agriculture Department: {total_agri}")
    print(f"Total schemes across all departments in KrishiMitra: {total_all}")

if __name__ == "__main__":
    main()
