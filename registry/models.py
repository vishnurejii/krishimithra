"""
Data models and Enums for Department & Source Registry, Scheme Classifications,
and Scheme Coverage Matrix.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date

class DepartmentCategory(str, Enum):
    CORE_AGRICULTURE = "Core Agriculture"
    ALLIED_AGRICULTURE = "Allied Agriculture"
    RURAL_AND_LOCAL_GOV = "Rural & Local Self Government"
    WELFARE_AND_CREDIT = "Welfare, Credit & Cooperation"
    WATER_AND_NATURAL_RESOURCES = "Water & Natural Resources"
    COMMODITY_BOARD = "Commodity Board"
    CENTRAL_MINISTRY = "Central Ministry / Scheme"
    LINE_DEPARTMENT = "Line Department (Non-Agriculture)"

class InvestigationStatus(str, Enum):
    NOT_INVESTIGATED = "Not investigated"
    INVESTIGATING = "Investigating"
    DOCUMENTS_COLLECTED = "Documents collected"
    SCHEMES_EXTRACTED = "Schemes extracted"
    VERIFICATION_PENDING = "Verification pending"
    VERIFIED = "Verified"
    NO_RELEVANT_SCHEMES_FOUND = "No relevant schemes found"

class SchemeClassification(str, Enum):
    GOVERNMENT_SCHEME = "Government Scheme"
    GOVERNMENT_SERVICE = "Government Service"
    SUBSIDY = "Subsidy"
    PENSION_WELFARE = "Pensions and welfare benefits for agricultural workers"
    AGRICULTURAL_LOAN = "Agricultural loan"
    INSURANCE = "Insurance"
    RESEARCH_TRAINING = "Research and training programme"
    MARKET_SUPPORT = "Market support and price incentive"

class SchemeStatus(str, Enum):
    PROPOSED = "Proposed"
    APPROVED = "Approved"
    ACTIVE = "Active"
    EXPIRED = "Expired"
    DISCONTINUED = "Discontinued"
    VERIFICATION_PENDING = "Verification Pending"

class GovernmentDepartmentModel(BaseModel):
    id: str
    name: str
    malayalam_name: Optional[str] = None
    level: str = "State" # State, Central, District, Local-Body
    category: DepartmentCategory
    official_website: str
    scheme_listing_url: Optional[str] = None
    portal_type: str = "Department"
    has_agriculture_schemes: bool = True
    investigation_status: InvestigationStatus = InvestigationStatus.NOT_INVESTIGATED
    documents_discovered: int = 0
    schemes_identified: int = 0
    active_schemes_verified: int = 0
    expired_schemes: int = 0
    sources_accessible: bool = True
    missing_information: Optional[str] = None
    last_checked_date: Optional[str] = None
    notes: Optional[str] = None

class SchemeCoverageEntry(BaseModel):
    department_id: str
    department_name: str
    category: str
    official_website: str
    scheme_url: Optional[str]
    investigation_status: InvestigationStatus
    documents_discovered: int
    schemes_identified: int
    active_verified: int
    expired_count: int
    is_accessible: bool
    missing_info: Optional[str]
    last_checked: Optional[str]
