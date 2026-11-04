"""
Pydantic Schemas for AI-based Scheme Information Extraction in KrishiMitra AI.
Enforces strict JSON schema, null defaults, page citations, and confidence tracking.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ExtractedSchemeInformation(BaseModel):
    # Core Scheme Identification
    scheme_name: str = Field(description="Official name of the scheme in English")
    malayalam_name: Optional[str] = Field(default=None, description="Official name of scheme in Malayalam if present")
    scheme_code: Optional[str] = Field(default=None, description="Official scheme code or order number")
    classification: str = Field(
        default="Government Scheme",
        description="One of: Government Scheme, Government Service, Subsidy, Pensions and welfare benefits for agricultural workers, Agricultural loan, Insurance, Research and training programme, Market support and price incentive"
    )
    scheme_status: str = Field(
        default="Verification Pending",
        description="One of: Proposed, Approved, Active, Expired, Discontinued, Verification Pending"
    )
    government_department: str = Field(description="Name of the nodal government department or board")
    government_level: str = Field(default="State", description="State, Central, CSS (Centrally Sponsored), District, or Local Body")
    scheme_objective: Optional[str] = Field(default=None, description="Stated objective and purpose of the scheme")
    scheme_description: Optional[str] = Field(default=None, description="Detailed summary description of the scheme")

    # Eligibility Criteria
    beneficiary_categories: List[str] = Field(default_factory=list, description="Target groups, e.g., Small Farmer, Marginal Farmer, Women, Youth, SC, ST, General")
    eligible_farmer_types: List[str] = Field(default_factory=list, description="E.g., Owner cultivator, Tenant farmer, Kudumbashree JLG, Leaseholder")
    min_land_acres: Optional[float] = Field(default=None, description="Minimum landholding requirement in acres, or null if no minimum")
    max_land_acres: Optional[float] = Field(default=None, description="Maximum landholding ceiling in acres, or null if no ceiling")
    income_limit: Optional[float] = Field(default=None, description="Annual income cap in INR, or null if no income ceiling")
    caste_category: Optional[str] = Field(default=None, description="General, OBC, SC, ST, or null if universal")
    residency_requirements: Optional[str] = Field(default=None, description="Resident of Kerala, specific Panchayat, etc.")
    important_conditions: List[str] = Field(default_factory=list, description="Mandatory terms and conditions")
    exclusions: List[str] = Field(default_factory=list, description="Categories excluded from eligibility")

    # Benefits & Subsidies
    benefit_type: Optional[str] = Field(default=None, description="Direct Cash, Input Subsidy, Capital Subsidy, Interest Subvention, Equipment Subsidy")
    subsidy_amount: Optional[float] = Field(default=None, description="Fixed subsidy in INR if applicable")
    subsidy_percentage: Optional[float] = Field(default=None, description="Percentage subsidy of total project cost (e.g. 50.0)")
    max_assistance_limit: Optional[float] = Field(default=None, description="Maximum cap limit in INR")
    unit_of_assistance: Optional[str] = Field(default=None, description="Per acre, per hectare, per unit, per farmer")
    disbursement_mode: Optional[str] = Field(default=None, description="DBT to bank account, seed agency, kind/inputs")

    # Target Crops & Geographic Coverage
    eligible_crops: List[str] = Field(default_factory=list, description="E.g., Paddy, Coconut, Pepper, Cardamom, Banana, Vegetables")
    applicable_districts: List[str] = Field(default_factory=list, description="List of Kerala districts, or ['All Kerala'] if statewide")

    # Application Process
    application_procedure: Optional[str] = Field(default=None, description="Step by step application procedure")
    official_application_portal: Optional[str] = Field(default=None, description="URL of application portal (e.g. AIMS, PM-KISAN, Service Plus)")
    required_documents: List[str] = Field(default_factory=list, description="Checklist: Aadhaar, Land Tax Receipt, Possession Certificate, etc.")
    application_start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD or null")
    application_deadline: Optional[str] = Field(default=None, description="YYYY-MM-DD or null")
    contact_details: Optional[str] = Field(default=None, description="Krishi Bhavan, Helpline number, Email")

    # Provenance & Verification
    source_document_name: str = Field(description="Name or file path of the source government document")
    source_page_numbers: List[int] = Field(default_factory=list, description="Page numbers where facts were cited")
    is_confirmed: bool = Field(default=True, description="True if directly confirmed from official text, False if inferred")
    conflict_detected: bool = Field(default=False, description="True if this order contradicts an existing order")
    confidence_score: float = Field(default=0.95, description="Confidence score between 0.0 and 1.0")
