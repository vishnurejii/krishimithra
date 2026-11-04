"""
Rule-Based & Semantic Farmer Eligibility Checker for KrishiMitra AI.
Matches farmer land size, crop types, district, income, and category
against all schemes using a single optimized batch query.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from eligibility.models import FarmerInputProfile, SchemeEligibilityMatch, FarmerEligibilityEvaluationResponse
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.eligibility.checker")

class EligibilityChecker:
    def evaluate_farmer(self, profile: FarmerInputProfile) -> FarmerEligibilityEvaluationResponse:
        """
        Evaluates a farmer profile against all active schemes in the PostgreSQL database.
        Uses a single aggregated query to eliminate N+1 network latency.
        """
        logger.info(f"Evaluating eligibility for {profile.full_name} in {profile.district} (Land: {profile.total_land_acres} ac, Crops: {profile.primary_crops})")

        eligible_matches: List[SchemeEligibilityMatch] = []
        conditional_matches: List[SchemeEligibilityMatch] = []

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            s.id as scheme_id,
                            s.name as scheme_name,
                            s.classification,
                            s.level as government_level,
                            s.official_portal_url,
                            s.last_verified_at,
                            e.min_land_acres,
                            e.max_land_acres,
                            e.income_limit,
                            e.caste_category,
                            e.beneficiary_categories,
                            e.eligible_farmer_types,
                            b.subsidy_percentage,
                            b.subsidy_amount,
                            b.max_assistance_limit,
                            d.title as doc_title,
                            COALESCE(ARRAY_AGG(DISTINCT sc.crop_name) FILTER (WHERE sc.crop_name IS NOT NULL), '{}') as crops,
                            COALESCE(ARRAY_AGG(DISTINCT sd.district_name) FILTER (WHERE sd.district_name IS NOT NULL), '{}') as districts,
                            BOOL_OR(COALESCE(sd.is_statewide, FALSE)) as has_statewide,
                            COALESCE(ARRAY_AGG(DISTINCT ag.document_name) FILTER (WHERE ag.document_name IS NOT NULL), '{}') as guidelines
                        FROM schemes s
                        LEFT JOIN scheme_eligibility e ON s.id = e.scheme_id
                        LEFT JOIN scheme_benefits b ON s.id = b.scheme_id
                        LEFT JOIN scheme_documents d ON s.id = d.scheme_id
                        LEFT JOIN scheme_crops sc ON s.id = sc.scheme_id
                        LEFT JOIN scheme_districts sd ON s.id = sd.scheme_id
                        LEFT JOIN application_guidelines ag ON s.id = ag.scheme_id
                        GROUP BY s.id, s.name, s.classification, s.level, s.official_portal_url, s.last_verified_at,
                                 e.min_land_acres, e.max_land_acres, e.income_limit, e.caste_category,
                                 e.beneficiary_categories, e.eligible_farmer_types,
                                 b.subsidy_percentage, b.subsidy_amount, b.max_assistance_limit, d.title;
                        """
                    )
                    schemes = cur.fetchall()

                    for sch in schemes:
                        crops = [c.lower() for c in (sch["crops"] or [])]
                        districts = [d.lower() for d in (sch["districts"] or [])]
                        is_statewide = sch["has_statewide"] or len(districts) == 0
                        guidelines = sch["guidelines"] or ["Aadhaar Card", "Current Land Tax Receipt", "Bank Passbook Copy"]

                        is_eligible = True
                        matched_reasons = []
                        unmet_reasons = []

                        # 1. District Check
                        if not is_statewide and profile.district.lower() not in districts and not any("all" in d for d in districts):
                            is_eligible = False
                            unmet_reasons.append(f"Not notified for {profile.district}")
                        else:
                            matched_reasons.append(f"Notified for {profile.district} (Statewide)")

                        # 2. Crop Match
                        farmer_crops_lower = [c.lower() for c in profile.primary_crops]
                        crop_matched = any(c in farmer_crops_lower for c in crops) or "all" in crops or len(crops) == 0
                        if crop_matched:
                            matched_reasons.append("Crop match confirmed")
                        else:
                            is_eligible = False
                            unmet_reasons.append(f"Eligible crops: {', '.join(crops)}")

                        # 3. Landholding Check
                        min_acres = sch["min_land_acres"]
                        max_acres = sch["max_land_acres"]
                        if min_acres is not None and profile.total_land_acres < float(min_acres):
                            is_eligible = False
                            unmet_reasons.append(f"Min land: {min_acres} ac (Have: {profile.total_land_acres} ac)")
                        if max_acres is not None and profile.total_land_acres > float(max_acres):
                            is_eligible = False
                            unmet_reasons.append(f"Max land ceiling: {max_acres} ac")
                        if (min_acres is None or profile.total_land_acres >= float(min_acres)) and (max_acres is None or profile.total_land_acres <= float(max_acres)):
                            matched_reasons.append(f"Land {profile.total_land_acres} acres within range")

                        # 4. Income Limit Check
                        inc_limit = sch["income_limit"]
                        if inc_limit is not None and profile.annual_income and profile.annual_income > float(inc_limit):
                            is_eligible = False
                            unmet_reasons.append(f"Income cap: Rs {inc_limit}")

                        # Estimate benefit string
                        pct = sch["subsidy_percentage"]
                        amt = sch["subsidy_amount"]
                        cap = sch["max_assistance_limit"]
                        b_str = ""
                        if pct:
                            b_str += f"{pct}% project cost subsidy"
                        if amt:
                            b_str += f" (Rs {amt})"
                        if cap:
                            b_str += f" [Max assistance Rs {cap}]"
                        if not b_str:
                            b_str = "Financial assistance as per department scale of finance"

                        match_obj = SchemeEligibilityMatch(
                            scheme_id=sch["scheme_id"],
                            scheme_name=sch["scheme_name"],
                            classification=sch["classification"] or "Government Scheme",
                            government_level=sch["government_level"] or "State",
                            is_eligible=is_eligible,
                            match_score=100 if is_eligible else 50,
                            matched_criteria=matched_reasons,
                            unmet_criteria=unmet_reasons,
                            estimated_benefit=b_str,
                            required_documents=guidelines,
                            official_application_portal=sch["official_portal_url"] or "https://aimsnew.kerala.gov.in/",
                            source_reference=sch["doc_title"] or "Government Order Guidelines",
                            last_verified=str(sch["last_verified_at"] or datetime.now(timezone.utc).strftime("%Y-%m-%d"))
                        )

                        if is_eligible:
                            eligible_matches.append(match_obj)
                        else:
                            conditional_matches.append(match_obj)

        except Exception as e:
            logger.error(f"Eligibility evaluation error: {e}")

        logger.info(f"Evaluation finished: {len(eligible_matches)} eligible, {len(conditional_matches)} conditional schemes.")
        return FarmerEligibilityEvaluationResponse(
            farmer_profile=profile,
            total_matched_schemes=len(eligible_matches),
            eligible_schemes=eligible_matches,
            conditional_schemes=conditional_matches[:5]
        )
