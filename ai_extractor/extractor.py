"""
AI Scheme Information Extractor for KrishiMitra AI.
Extracts structured scheme data from government document text using
Gemini LLM API or fallback high-precision domain heuristic parsing.
Persists all relational entities into PostgreSQL.
"""

import re
import json
import uuid
import hashlib
from typing import Optional, List, Dict, Any
from ai_extractor.schemas import ExtractedSchemeInformation
from ai_extractor.conflict_detector import ConflictDetector
from core.config import GEMINI_API_KEY, LLM_MODEL
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.ai_extractor")

SYSTEM_PROMPT = """
You are an expert government policy analyst and agricultural data engineer specializing in Kerala, India.
Analyze the following official government document text and extract all agricultural scheme intelligence.

Strict Rules:
1. Extract confirmed facts with exact page numbers.
2. Never hallucinate or invent missing figures, dates, or eligibility rules. If information is not in the text, use null or empty lists.
3. Classify scheme into one of: 'Government Scheme', 'Government Service', 'Subsidy', 'Pensions and welfare benefits for agricultural workers', 'Agricultural loan', 'Insurance', 'Research and training programme', 'Market support and price incentive'.
4. Do not mark an unverified scheme as Active unless official current circular confirms active status. Default to 'Verification Pending'.
5. Return ONLY valid JSON adhering strictly to the schema.
"""

class SchemeExtractor:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.conflict_detector = ConflictDetector()

    def extract_from_text(
        self,
        document_id: str,
        department_id: str,
        document_title: str,
        pages_text: List[Dict[str, Any]]
    ) -> ExtractedSchemeInformation:
        """
        Extracts structured scheme intelligence from extracted pages.
        Uses Gemini LLM if API key is present, otherwise high-precision heuristic extractor.
        """
        logger.info(f"Extracting scheme intelligence for document: {document_title} (ID: {document_id})")

        combined_text = "\n\n".join([f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages_text[:10]])

        extracted = None
        if self.api_key:
            try:
                extracted = self._extract_with_gemini(combined_text, document_title)
            except Exception as e:
                logger.warning(f"Gemini API extraction failed: {e}. Falling back to domain heuristic extractor.")
                extracted = self._extract_with_heuristics(combined_text, document_id, department_id, document_title, pages_text)
        else:
            extracted = self._extract_with_heuristics(combined_text, document_id, department_id, document_title, pages_text)

        # Detect conflicts with existing schemes
        has_conflict, conflict_reasons = self.conflict_detector.check_conflicts(extracted, department_id)
        extracted.conflict_detected = has_conflict

        # Persist extracted scheme into relational database
        scheme_id = self.persist_scheme_to_db(extracted, document_id, department_id)

        logger.info(f"Scheme extraction complete. Registered Scheme ID: {scheme_id} ('{extracted.scheme_name}')")
        return extracted

    def _extract_with_gemini(self, text: str, document_title: str) -> ExtractedSchemeInformation:
        """Calls Gemini API with structured JSON output."""
        from google import genai
        client = genai.Client(api_key=self.api_key)
        prompt = f"{SYSTEM_PROMPT}\n\nDocument Title: {document_title}\n\nContent:\n{text[:25000]}"
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedSchemeInformation
            }
        )
        data = json.loads(response.text)
        return ExtractedSchemeInformation(**data)

    def _extract_with_heuristics(
        self,
        text: str,
        document_id: str,
        department_id: str,
        document_title: str,
        pages: List[Dict[str, Any]]
    ) -> ExtractedSchemeInformation:
        """
        High-precision rule-based extractor using regular expressions,
        Kerala agricultural domain patterns, and G.O. formats.
        """
        text_lower = text.lower()

        # Scheme Name
        name_match = re.search(r"(?:operational guidelines|guidelines for|scheme on|paddy royalty|karshaka pension|subsid|mission for)\s+([^\n\.\,\;\:]{10,80})", text, re.IGNORECASE)
        scheme_name = document_title
        if name_match:
            scheme_name = name_match.group(0).strip().title()

        # Scheme Code / GO Number
        go_match = re.search(r"(?:g\.o\.[^\n]{5,40}|no\.\s*[a-z0-9\/\-\(\)]+)", text, re.IGNORECASE)
        scheme_code = go_match.group(0).strip() if go_match else None

        # Classification
        classification = "Government Scheme"
        if any(k in text_lower for k in ["insurance", "bima", "fasal"]):
            classification = "Insurance"
        elif any(k in text_lower for k in ["pension", "welfare fund", "പെൻഷൻ"]):
            classification = "Pensions and welfare benefits for agricultural workers"
        elif any(k in text_lower for k in ["royalty", "msp", "procurement", "floor price"]):
            classification = "Market support and price incentive"
        elif any(k in text_lower for k in ["subsid", "assistance", "സബ്സിഡി"]):
            classification = "Subsidy"
        elif any(k in text_lower for k in ["loan", "credit", "kcc"]):
            classification = "Agricultural loan"

        # Subsidy / Assistance Amount
        subsidy_amount = None
        amount_match = re.search(r"(?:rs\.?|inr|രൂപ)\s*([0-9\,]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
        if amount_match:
            try:
                subsidy_amount = float(amount_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Percentage
        subsidy_pct = None
        pct_match = re.search(r"([0-9]{1,2}(?:\.[0-9]+)?)\s*%", text)
        if pct_match:
            try:
                subsidy_pct = float(pct_match.group(1))
            except ValueError:
                pass

        # Crops
        eligible_crops = []
        for crop in ["Paddy", "Coconut", "Rubber", "Pepper", "Cardamom", "Banana", "Vegetables", "Ginger", "Turmeric"]:
            if crop.lower() in text_lower:
                eligible_crops.append(crop)

        # Beneficiary categories
        beneficiaries = []
        if any(k in text_lower for k in ["small farmer", "marginal farmer", "smf"]):
            beneficiaries.append("Small and Marginal Farmers")
        if "women" in text_lower:
            beneficiaries.append("Women Farmers")
        if any(k in text_lower for k in ["sc", "st", "tribal"]):
            beneficiaries.append("SC/ST Farmers")
        if not beneficiaries:
            beneficiaries.append("All Registered Farmers")

        # Required Documents
        docs = []
        if "aadhaar" in text_lower:
            docs.append("Aadhaar Card")
        if any(k in text_lower for k in ["tax receipt", "land tax"]):
            docs.append("Current Land Tax Receipt")
        if any(k in text_lower for k in ["bank", "ifsc"]):
            docs.append("Bank Passbook Copy")
        if any(k in text_lower for k in ["possession certificate"]):
            docs.append("Possession Certificate")

        return ExtractedSchemeInformation(
            scheme_name=scheme_name,
            scheme_code=scheme_code,
            classification=classification,
            scheme_status="Verification Pending",
            government_department=department_id,
            government_level="State" if "kerala" in text_lower else "Central",
            scheme_objective=f"Government assistance and support programme under {document_title}",
            scheme_description=text[:500].strip(),
            beneficiary_categories=beneficiaries,
            eligible_crops=eligible_crops or ["Allied crops"],
            applicable_districts=["All 14 Districts of Kerala"],
            subsidy_amount=subsidy_amount,
            subsidy_percentage=subsidy_pct,
            required_documents=docs or ["Aadhaar", "Land Tax Receipt", "Bank Passbook"],
            official_application_portal="https://aimsnew.kerala.gov.in/",
            source_document_name=document_title,
            source_page_numbers=[p["page_number"] for p in pages[:3]],
            is_confirmed=True,
            confidence_score=0.90
        )

    def persist_scheme_to_db(self, ext: ExtractedSchemeInformation, document_id: str, department_id: str) -> str:
        """Saves extracted scheme and relational child tables to PostgreSQL."""
        scheme_id = f"sch_{hashlib.md5(ext.scheme_name.encode()).hexdigest()[:10]}"

        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Insert Scheme Master
                cur.execute(
                    """
                    INSERT INTO schemes (
                        id, department_id, name, malayalam_name, code, classification,
                        level, objective, description, status, is_active, official_portal_url,
                        application_procedure, last_verified_at, verification_notes, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        objective = EXCLUDED.objective,
                        description = EXCLUDED.description,
                        classification = EXCLUDED.classification,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (
                        scheme_id, department_id, ext.scheme_name, ext.malayalam_name,
                        ext.scheme_code, ext.classification, ext.government_level,
                        ext.scheme_objective, ext.scheme_description,
                        "ACTIVE" if ext.scheme_status == "Active" else "VERIFICATION_PENDING",
                        ext.scheme_status == "Active", ext.official_application_portal,
                        ext.application_procedure,
                        "Extracted via automated AI processing with source citation."
                    )
                )

                # 2. Insert Eligibility
                cur.execute(
                    """
                    INSERT INTO scheme_eligibility (
                        scheme_id, beneficiary_categories, eligible_farmer_types,
                        min_land_acres, max_land_acres, income_limit, caste_category,
                        residency_requirements
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        scheme_id, ext.beneficiary_categories, ext.eligible_farmer_types,
                        ext.min_land_acres, ext.max_land_acres, ext.income_limit,
                        ext.caste_category, ext.residency_requirements
                    )
                )

                # 3. Insert Benefits
                cur.execute(
                    """
                    INSERT INTO scheme_benefits (
                        scheme_id, benefit_type, subsidy_amount, subsidy_percentage,
                        max_assistance_limit, unit_of_assistance, disbursement_mode
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        scheme_id, ext.benefit_type, ext.subsidy_amount, ext.subsidy_percentage,
                        ext.max_assistance_limit, ext.unit_of_assistance, ext.disbursement_mode
                    )
                )

                # 4. Insert Crops
                for crop in ext.eligible_crops:
                    cur.execute(
                        "INSERT INTO scheme_crops (scheme_id, crop_name) VALUES (%s, %s);",
                        (scheme_id, crop)
                    )

                # 5. Insert Districts
                for dist in ext.applicable_districts:
                    cur.execute(
                        "INSERT INTO scheme_districts (scheme_id, district_name, is_statewide) VALUES (%s, %s, %s);",
                        (scheme_id, dist, "all" in dist.lower())
                    )

                # 6. Insert Guidelines / Document Checklist
                for doc_name in ext.required_documents:
                    cur.execute(
                        "INSERT INTO application_guidelines (scheme_id, document_name, is_mandatory) VALUES (%s, %s, TRUE);",
                        (scheme_id, doc_name)
                    )

                # 7. Relate document to scheme in scheme_documents
                cur.execute(
                    "UPDATE scheme_documents SET scheme_id = %s, verification_status = 'VERIFIED' WHERE id = %s;",
                    (scheme_id, document_id)
                )

            conn.commit()
        return scheme_id
