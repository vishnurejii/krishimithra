"""
Official Agriculture & Farmer Schemes Registry for KrishiMitra AI.
Contains strictly the verified Government Departments, Statutory Commodity Boards,
and Central Ministries that administer schemes, subsidies, loans, and welfare benefits
for agriculture and farmers in Kerala.
"""

from registry.models import DepartmentCategory, InvestigationStatus

DEPARTMENTS_REGISTRY = [
    # =========================================================================
    # CORE & ALLIED KERALA STATE AGRICULTURE DEPARTMENTS
    # =========================================================================
    {
        "id": "KL_AGRI_DEPT",
        "name": "Agriculture Development and Farmers' Welfare Department",
        "malayalam_name": "കൃഷിവകുപ്പും കർഷകക്ഷേമവും",
        "level": "State",
        "category": DepartmentCategory.CORE_AGRICULTURE,
        "official_website": "https://keralaagriculture.gov.in/",
        "scheme_listing_url": "https://keralaagriculture.gov.in/en/schemes/",
        "portal_type": "Department",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Primary state nodal department for agriculture, paddy royalties, input subsidies, state plan schemes."
    },
    {
        "id": "KL_AIMS_PORTAL",
        "name": "AIMS Kerala (Agricultural Information Management System)",
        "malayalam_name": "എയിംസ് കേരള - കർഷക സേവന പോർട്ടൽ",
        "level": "State",
        "category": DepartmentCategory.CORE_AGRICULTURE,
        "official_website": "https://aimsnew.kerala.gov.in/",
        "scheme_listing_url": "https://aimsnew.kerala.gov.in/",
        "portal_type": "Digital Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "State online farmer registration portal for Royalty, Crop Damage Compensation, Crop Insurance, and Subsidies."
    },
    {
        "id": "KL_KATHIR_PORTAL",
        "name": "KATHIR Kerala (Agri Technology Hub & Information Repository)",
        "malayalam_name": "കതിർ കേരള സംയോജിത കാർഷിക പ്ലാറ്റ്‌ഫോം",
        "level": "State",
        "category": DepartmentCategory.CORE_AGRICULTURE,
        "official_website": "https://kathir.kerala.gov.in/",
        "scheme_listing_url": "https://kathir.kerala.gov.in/",
        "portal_type": "Digital Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Integrated Kerala agriculture platform for digital farmer profiles, soil health, and scheme delivery."
    },
    {
        "id": "KL_AHD_DEPT",
        "name": "Animal Husbandry Department, Kerala",
        "malayalam_name": "മൃഗസംരക്ഷണ വകുപ്പ്",
        "level": "State",
        "category": DepartmentCategory.ALLIED_AGRICULTURE,
        "official_website": "https://ahd.kerala.gov.in/",
        "scheme_listing_url": "https://ahd.kerala.gov.in/schemes/",
        "portal_type": "Department",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Livestock subsidies, commercial dairy farm incentives, calf rearing, mobile veterinary clinics, disease control."
    },
    {
        "id": "KL_DAIRY_DEPT",
        "name": "Dairy Development Department, Kerala",
        "malayalam_name": "ക്ഷീരവികസന വകുപ്പ്",
        "level": "State",
        "category": DepartmentCategory.ALLIED_AGRICULTURE,
        "official_website": "https://dairydevelopment.kerala.gov.in/",
        "scheme_listing_url": "https://dairydevelopment.kerala.gov.in/schemes",
        "portal_type": "Department",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Milch animal induction subsidies, cattle feed assistance, silage making, dairy cooperative incentives."
    },
    {
        "id": "KL_FISHERIES_DEPT",
        "name": "Fisheries and Ports Department, Kerala",
        "malayalam_name": "ഫിഷറീസ് വകുപ്പ്",
        "level": "State",
        "category": DepartmentCategory.ALLIED_AGRICULTURE,
        "official_website": "https://fisheries.kerala.gov.in/",
        "scheme_listing_url": "https://fisheries.kerala.gov.in/schemes",
        "portal_type": "Department",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Inland aquaculture, biofloc fish farming, cage culture, ornamental fisheries and farmer welfare."
    },
    {
        "id": "KL_SOIL_CONS_DEPT",
        "name": "Soil Survey and Soil Conservation Department",
        "malayalam_name": "മണ്ണ് പര്യവേക്ഷണ - മണ്ണ് സംരക്ഷണ വകുപ്പ്",
        "level": "State",
        "category": DepartmentCategory.WATER_AND_NATURAL_RESOURCES,
        "official_website": "https://www.keralasoils.gov.in/",
        "scheme_listing_url": "https://www.keralasoils.gov.in/schemes",
        "portal_type": "Department",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Watershed development, soil testing, contour bunding, ravine reclamation, soil health cards."
    },
    {
        "id": "KL_COOPERATION_DEPT",
        "name": "Co-operation Department, Kerala",
        "malayalam_name": "സഹകരണ വകുപ്പ്",
        "level": "State",
        "category": DepartmentCategory.WELFARE_AND_CREDIT,
        "official_website": "https://cooperation.kerala.gov.in/",
        "scheme_listing_url": "https://cooperation.kerala.gov.in/schemes/",
        "portal_type": "Department",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "PACS agricultural credit, Kerala Bank short-term crop loans, interest subvention, debt relief."
    },
    {
        "id": "KL_KSCARDB",
        "name": "Kerala State Co-operative Agricultural & Rural Development Bank",
        "malayalam_name": "കേരള സംസ്ഥാന സഹകരണ കാർഷിക ഗ്രാമവികസന ബാങ്ക്",
        "level": "State",
        "category": DepartmentCategory.WELFARE_AND_CREDIT,
        "official_website": "https://kscardb.com/",
        "scheme_listing_url": "https://kscardb.com/schemes/",
        "portal_type": "Financial Institution",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Long-term farm development loans, plantation development, farm mechanization credit."
    },
    {
        "id": "KL_KUDUMBASHREE",
        "name": "Kudumbashree State Mission (Agriculture Wing)",
        "malayalam_name": "കുടുംബശ്രീ സംസ്ഥാന മിഷൻ (കാർഷിക വിഭാഗം)",
        "level": "State",
        "category": DepartmentCategory.RURAL_AND_LOCAL_GOV,
        "official_website": "https://kudumbashree.org/",
        "scheme_listing_url": "https://kudumbashree.org/pages/53",
        "portal_type": "State Mission",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Joint Liability Groups (JLGs), collective farming interest subventions, fallow-land farming subsidies."
    },
    {
        "id": "KL_KAU_ACAD",
        "name": "Kerala Agricultural University (KAU)",
        "malayalam_name": "കേരള കാർഷിക സർവകലാശാല",
        "level": "State/Academic",
        "category": DepartmentCategory.CORE_AGRICULTURE,
        "official_website": "https://kau.in/",
        "scheme_listing_url": "https://kau.in/programmes",
        "portal_type": "University",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Seed distribution schemes, training programmes, Krishi Vigyan Kendras (KVK), bio-control inputs."
    },
    {
        "id": "KL_VFPCK",
        "name": "Vegetable and Fruit Promotion Council Keralam (VFPCK)",
        "malayalam_name": "വെജിറ്റബിൾ ആന്റ് ഫ്രൂട്ട് പ്രമോഷൻ കൗൺസിൽ",
        "level": "State",
        "category": DepartmentCategory.CORE_AGRICULTURE,
        "official_website": "https://vfpck.org/",
        "scheme_listing_url": "https://vfpck.org/schemes",
        "portal_type": "Statutory Council",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Self Help Groups (SHG) credit, vegetable production clusters, markets and base price support."
    },
    {
        "id": "KL_HORTICORP",
        "name": "Kerala State Horticultural Products Development Corporation (Horticorp)",
        "malayalam_name": "ഹോർട്ടികോർപ്പ്",
        "level": "State",
        "category": DepartmentCategory.CORE_AGRICULTURE,
        "official_website": "https://horticorp.kerala.gov.in/",
        "scheme_listing_url": "https://horticorp.kerala.gov.in/schemes",
        "portal_type": "Public Undertaking",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Honey mission subsidies, procurement at floor price, marketing of vegetables and fruit."
    },

    # =========================================================================
    # STATUTORY COMMODITY BOARDS (CENTRAL & KERALA REGIONAL HUBS)
    # =========================================================================
    {
        "id": "BD_RUBBER",
        "name": "Rubber Board India",
        "malayalam_name": "റബ്ബർ ബോർഡ്",
        "level": "Central/Board",
        "category": DepartmentCategory.COMMODITY_BOARD,
        "official_website": "https://rubberboard.gov.in/",
        "scheme_listing_url": "https://rubberboard.gov.in/public/schemes",
        "portal_type": "Statutory Board",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Rubber replanting subsidy, Rubber Production Incentives Scheme (RPIS Kerala), rain-guarding subsidy."
    },
    {
        "id": "BD_COCONUT",
        "name": "Coconut Development Board (Kochi)",
        "malayalam_name": "നാളികേര വികസന ബോർഡ്",
        "level": "Central/Board",
        "category": DepartmentCategory.COMMODITY_BOARD,
        "official_website": "https://coconutboard.gov.in/",
        "scheme_listing_url": "https://coconutboard.gov.in/scheme.aspx",
        "portal_type": "Statutory Board",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Replanting and rejuvenation of diseased palms, TMOC processing subsidies, Kera Suraksha insurance, nursery aid."
    },
    {
        "id": "BD_SPICES",
        "name": "Spices Board India (Kochi)",
        "malayalam_name": "സ്പൈസസ് ബോർഡ്",
        "level": "Central/Board",
        "category": DepartmentCategory.COMMODITY_BOARD,
        "official_website": "https://indianspices.com/",
        "scheme_listing_url": "https://indianspices.com/schemes",
        "portal_type": "Statutory Board",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Small cardamom replanting, pepper rejuvenation, irrigation equipment subsidy, organic spice certification."
    },
    {
        "id": "BD_COFFEE",
        "name": "Coffee Board of India (Wayanad / Kerala Region)",
        "malayalam_name": "കോഫി ബോർഡ്",
        "level": "Central/Board",
        "category": DepartmentCategory.COMMODITY_BOARD,
        "official_website": "https://coffeeboard.gov.in/",
        "scheme_listing_url": "https://coffeeboard.gov.in/schemes.html",
        "portal_type": "Statutory Board",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Wayanad Robusta coffee development, water augmentation, mechanization, replanting subsidies."
    },
    {
        "id": "BD_NABARD",
        "name": "NABARD Kerala Regional Office",
        "malayalam_name": "നബാർഡ് കേരളം",
        "level": "Central/Financial",
        "category": DepartmentCategory.WELFARE_AND_CREDIT,
        "official_website": "https://www.nabard.org/",
        "scheme_listing_url": "https://www.nabard.org/content.aspx?id=597",
        "portal_type": "Development Bank",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "FPO promotion, Watershed development, RIDF infrastructure, Agri-Clinic and Agri-Business scheme."
    },

    # =========================================================================
    # CENTRAL GOVERNMENT AGRICULTURE SCHEMES APPLICABLE TO KERALA
    # =========================================================================
    {
        "id": "CEN_PM_KISAN",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "malayalam_name": "പി.എം. കിസാൻ സമ്മാൻ നിധി",
        "level": "Central",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://pmkisan.gov.in/",
        "scheme_listing_url": "https://pmkisan.gov.in/",
        "portal_type": "Central Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Rs 6,000/year income support delivered in 3 equal installments via DBT to landholding farmers in Kerala."
    },
    {
        "id": "CEN_PMFBY",
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "malayalam_name": "പ്രധാനമന്ത്രി ഫസൽ ബീമാ യോജന",
        "level": "Central/State Share",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://pmfby.gov.in/",
        "scheme_listing_url": "https://pmfby.gov.in/",
        "portal_type": "Insurance Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Yield-based comprehensive crop insurance notified for selected crops and seasons in Kerala."
    },
    {
        "id": "CEN_MIDH",
        "name": "Mission for Integrated Development of Horticulture (MIDH)",
        "malayalam_name": "സംയോജിത ഹോർട്ടികൾച്ചർ വികസന മിഷൻ",
        "level": "Central/CSS",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://midh.gov.in/",
        "scheme_listing_url": "https://midh.gov.in/",
        "portal_type": "Central Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Commercial horticulture, high-density banana, pineapple, polyhouses, mushrooms, and pack-houses in Kerala."
    },
    {
        "id": "CEN_AIF",
        "name": "Agriculture Infrastructure Fund (AIF)",
        "malayalam_name": "കാർഷിക അടിസ്ഥാന സൗകര്യ വികസന ഫണ്ട്",
        "level": "Central",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://agriinfra.dac.gov.in/",
        "scheme_listing_url": "https://agriinfra.dac.gov.in/",
        "portal_type": "Central Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Long-term debt financing up to Rs 2 Crores with 3% interest subvention for post-harvest agri-infrastructure."
    },
    {
        "id": "CEN_SOIL_HEALTH",
        "name": "Soil Health Card Scheme",
        "malayalam_name": "സോയിൽ ഹെൽത്ത് കാർഡ് പദ്ധതി",
        "level": "Central/State Share",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://soilhealth.dac.gov.in/",
        "scheme_listing_url": "https://soilhealth.dac.gov.in/",
        "portal_type": "Central Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Soil test-based customized nutrient recommendations and soil health cards issued to farmers across Kerala."
    },
    {
        "id": "CEN_PM_KUSUM",
        "name": "PM-KUSUM (Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan)",
        "malayalam_name": "പി.എം. കുസും സോളാർ പമ്പ് പദ്ധതി",
        "level": "Central/State Share",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://pmkusum.mnre.gov.in/",
        "scheme_listing_url": "https://pmkusum.mnre.gov.in/",
        "portal_type": "Central Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Standalone solar agricultural pumps (up to 7.5 HP) subsidy for farmers with ANERT in Kerala."
    },
    {
        "id": "CEN_RKVY",
        "name": "Rashtriya Krishi Vikas Yojana (RKVY-RAFTAAR)",
        "malayalam_name": "രാഷ്ട്രീയ കൃഷി വികാസ് യോജന",
        "level": "Central/CSS",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://rkvy.nic.in/",
        "scheme_listing_url": "https://rkvy.nic.in/",
        "portal_type": "Central Portal",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.DOCUMENTS_COLLECTED,
        "notes": "Comprehensive agri-infrastructure, farm mechanization, seed production and value chain projects in Kerala."
    },
    {
        "id": "CEN_MISS_KCC",
        "name": "Modified Interest Subvention Scheme (MISS) & Kisan Credit Card (KCC)",
        "malayalam_name": "കിസാൻ ക്രെഡിറ്റ് കാർഡ് & പലിശ ഇളവ്",
        "level": "Central",
        "category": DepartmentCategory.CENTRAL_MINISTRY,
        "official_website": "https://agriwelfare.gov.in/",
        "scheme_listing_url": "https://agriwelfare.gov.in/",
        "portal_type": "Central Scheme",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Short term crop loan up to Rs 3 lakh at 4% effective interest rate for prompt paying farmers in Kerala."
    },

    # =========================================================================
    # ALLIED STATUTORY BOARDS WITH FARMER WELFARE SCHEMES
    # =========================================================================
    {
        "id": "KL_LABOUR",
        "name": "Labour and Skills Department (Kerala Agricultural Workers Welfare Fund)",
        "malayalam_name": "തൊഴിൽ വകുപ്പ് (കേരള കർഷകത്തൊഴിലാളി ക്ഷേമനിധി ബോർഡ്)",
        "level": "State",
        "category": DepartmentCategory.WELFARE_AND_CREDIT,
        "official_website": "https://labour.kerala.gov.in/",
        "scheme_listing_url": "https://labour.kerala.gov.in/",
        "portal_type": "Statutory Board",
        "has_agriculture_schemes": True,
        "investigation_status": InvestigationStatus.VERIFIED,
        "notes": "Administers Kerala Agricultural Workers Welfare Fund Board (KAWWFB) providing pensions and welfare grants."
    }
]
