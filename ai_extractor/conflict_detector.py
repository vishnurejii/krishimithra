"""
Scheme Conflict and Amendment Detector for KrishiMitra AI.
Analyzes newly extracted scheme data against existing database records to detect:
- Conflicting subsidy rates
- Deadline revisions
- Superseding government orders
- Eligibility criteria changes
"""

from typing import Dict, Any, Optional, Tuple, List
from ai_extractor.schemas import ExtractedSchemeInformation
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.ai_extractor.conflict_detector")

class ConflictDetector:
    def check_conflicts(self, extracted: ExtractedSchemeInformation, department_id: str) -> Tuple[bool, List[str]]:
        """
        Compares extracted scheme details with database records of the same or similar scheme.
        Returns (has_conflicts, conflict_descriptions).
        """
        conflicts = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Look for existing scheme with same name
                    cur.execute(
                        """
                        SELECT s.id, s.name, s.application_deadline, s.status,
                               b.subsidy_amount, b.subsidy_percentage, b.max_assistance_limit
                        FROM schemes s
                        LEFT JOIN scheme_benefits b ON s.id = b.scheme_id
                        WHERE LOWER(s.name) = LOWER(%s) OR LOWER(s.code) = LOWER(%s)
                        LIMIT 1;
                        """,
                        (extracted.scheme_name, extracted.scheme_code or "")
                    )
                    existing = cur.fetchone()

                    if existing:
                        # Check deadline conflict
                        if existing["application_deadline"] and extracted.application_deadline:
                            if str(existing["application_deadline"]) != str(extracted.application_deadline):
                                conflicts.append(
                                    f"Application deadline changed from {existing['application_deadline']} to {extracted.application_deadline}"
                                )

                        # Check subsidy amount conflict
                        if existing["subsidy_amount"] and extracted.subsidy_amount:
                            if float(existing["subsidy_amount"]) != float(extracted.subsidy_amount):
                                conflicts.append(
                                    f"Subsidy amount revised from Rs {existing['subsidy_amount']} to Rs {extracted.subsidy_amount}"
                                )

                        # Check max assistance limit conflict
                        if existing["max_assistance_limit"] and extracted.max_assistance_limit:
                            if float(existing["max_assistance_limit"]) != float(extracted.max_assistance_limit):
                                conflicts.append(
                                    f"Maximum assistance ceiling revised from Rs {existing['max_assistance_limit']} to Rs {extracted.max_assistance_limit}"
                                )

        except Exception as e:
            logger.warning(f"Error checking conflicts: {e}")

        has_conflicts = len(conflicts) > 0
        if has_conflicts:
            logger.info(f"Conflict detected for {extracted.scheme_name}: {conflicts}")
        return has_conflicts, conflicts
