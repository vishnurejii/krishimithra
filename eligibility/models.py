"""
Farmer Profile and Eligibility Evaluation Models for KrishiMitra AI.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

KERALA_DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
    "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
    "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
]

class FarmerInputProfile(BaseModel):
    full_name: Optional[str] = "Kerala Farmer"
    district: str = Field(description="One of the 14 Kerala districts")
    taluk: Optional[str] = None
    panchayat: Optional[str] = None
    farmer_type: str = Field(default="Small Farmer", description="Marginal Farmer (<2.5 acres), Small Farmer (2.5-5 acres), Large Farmer, Kudumbashree JLG, Tenant Farmer")
    total_land_acres: float = Field(default=1.0, description="Total cultivable landholding in acres")
    primary_crops: List[str] = Field(default_factory=list, description="E.g. Paddy, Pepper, Coconut, Banana")
    irrigation_type: Optional[str] = Field(default="Rainfed", description="Rainfed, Well, Canal, Drip/Sprinkler")
    annual_income: Optional[float] = Field(default=150000.0, description="Annual farm + non-farm income in INR")
    caste_category: Optional[str] = Field(default="General", description="General, OBC, SC, ST")
    has_kisan_credit_card: bool = False

class SchemeEligibilityMatch(BaseModel):
    scheme_id: str
    scheme_name: str
    classification: str
    government_level: str
    is_eligible: bool
    match_score: int = 100 # 0 to 100
    matched_criteria: List[str] = []
    unmet_criteria: List[str] = []
    estimated_benefit: str
    required_documents: List[str] = []
    official_application_portal: str
    source_reference: str
    last_verified: str

class FarmerEligibilityEvaluationResponse(BaseModel):
    farmer_profile: FarmerInputProfile
    total_matched_schemes: int
    eligible_schemes: List[SchemeEligibilityMatch] = []
    conditional_schemes: List[SchemeEligibilityMatch] = []
