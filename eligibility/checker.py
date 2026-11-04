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
        seen_scheme_ids: set = set()

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
                            MIN(e.min_land_acres) as min_land_acres,
                            MAX(e.max_land_acres) as max_land_acres,
                            MAX(e.income_limit) as income_limit,
                            MAX(e.caste_category) as caste_category,
                            MAX(b.subsidy_percentage) as subsidy_percentage,
                            MAX(b.subsidy_amount) as subsidy_amount,
                            MAX(b.max_assistance_limit) as max_assistance_limit,
                            (SELECT title FROM scheme_documents WHERE scheme_id = s.id AND title IS NOT NULL ORDER BY id LIMIT 1) as doc_title,
                            COALESCE((SELECT ARRAY_AGG(DISTINCT crop_name) FROM scheme_crops WHERE scheme_id = s.id), '{}') as crops,
                            COALESCE((SELECT ARRAY_AGG(DISTINCT district_name) FROM scheme_districts WHERE scheme_id = s.id), '{}') as districts,
                            COALESCE((SELECT BOOL_OR(is_statewide) FROM scheme_districts WHERE scheme_id = s.id), FALSE) as has_statewide,
                            COALESCE((SELECT ARRAY_AGG(DISTINCT document_name) FROM application_guidelines WHERE scheme_id = s.id), '{}') as guidelines,
                            COALESCE((SELECT ARRAY_AGG(DISTINCT ft) FROM scheme_eligibility se, LATERAL unnest(se.eligible_farmer_types) ft WHERE se.scheme_id = s.id), '{}') as eligible_farmer_types,
                            COALESCE((SELECT ARRAY_AGG(DISTINCT bc) FROM scheme_eligibility se, LATERAL unnest(se.beneficiary_categories) bc WHERE se.scheme_id = s.id), '{}') as beneficiary_categories
                        FROM schemes s
                        LEFT JOIN scheme_eligibility e ON s.id = e.scheme_id
                        LEFT JOIN scheme_benefits b ON s.id = b.scheme_id
                        WHERE s.is_active = TRUE OR s.status = 'ACTIVE'
                        GROUP BY s.id, s.name, s.classification, s.level, s.official_portal_url, s.last_verified_at
                        ORDER BY s.name ASC;
                        """
                    )
                    schemes = cur.fetchall()

                    for sch in schemes:
                        scheme_id = sch["scheme_id"]
                        if scheme_id in seen_scheme_ids:
                            continue
                        seen_scheme_ids.add(scheme_id)

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

                        # 5. Community / Caste Check
                        caste = sch["caste_category"]
                        if caste and caste.strip().upper() not in ["ALL", "GENERAL", "ANY", ""]:
                            farmer_caste = (profile.caste_category or "General").strip().upper()
                            if farmer_caste != caste.strip().upper():
                                is_eligible = False
                                unmet_reasons.append(f"Restricted to {caste} community")

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
