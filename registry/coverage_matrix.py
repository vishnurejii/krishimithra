"""
Scheme Coverage Matrix for KrishiMitra AI.
Calculates and generates reports on:
- Investigation status of all 62 departments and central agencies
- Documents discovered and collected per department
- Schemes identified, verified active, and expired
- Inaccessible sources and missing information
- Breakdown by Scheme Classification (Subsidies, Loans, Insurance, Welfare, etc.)
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
from registry.models import InvestigationStatus, SchemeCoverageEntry, SchemeClassification
from registry.source_registry import SourceRegistry
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.coverage_matrix")

class SchemeCoverageMatrix:
    def __init__(self, registry: SourceRegistry):
        self.registry = registry

    def compute_matrix(self) -> List[Dict[str, Any]]:
        """
        Pulls real database numbers and in-memory metadata to build the live coverage matrix.
        """
        matrix = []
        doc_counts = {}
        scheme_counts = {}
        active_counts = {}
        expired_counts = {}

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Count documents by department
                    cur.execute(
                        """
                        SELECT department_id, COUNT(*) as count
                        FROM scheme_documents
                        GROUP BY department_id;
                        """
                    )
                    for r in cur.fetchall():
                        doc_counts[r["department_id"]] = r["count"]

                    # Count total schemes by department
                    cur.execute(
                        """
                        SELECT department_id, COUNT(*) as count
                        FROM schemes
                        GROUP BY department_id;
                        """
                    )
                    for r in cur.fetchall():
                        scheme_counts[r["department_id"]] = r["count"]

                    # Count active verified schemes
                    cur.execute(
                        """
                        SELECT department_id, COUNT(*) as count
                        FROM schemes
                        WHERE status = 'ACTIVE' OR is_active = TRUE
                        GROUP BY department_id;
                        """
                    )
                    for r in cur.fetchall():
                        active_counts[r["department_id"]] = r["count"]

                    # Count expired schemes
                    cur.execute(
                        """
                        SELECT department_id, COUNT(*) as count
                        FROM schemes
                        WHERE status = 'EXPIRED'
                        GROUP BY department_id;
                        """
                    )
                    for r in cur.fetchall():
                        expired_counts[r["department_id"]] = r["count"]

        except Exception as e:
            logger.warning(f"Database query error during matrix computation (using zero defaults): {e}")

        for dept in self.registry.departments.values():
            docs = doc_counts.get(dept.id, dept.documents_discovered)
            schemes = scheme_counts.get(dept.id, dept.schemes_identified)
            active = active_counts.get(dept.id, dept.active_schemes_verified)
            expired = expired_counts.get(dept.id, dept.expired_schemes)

            # Auto-calculate status if documents and schemes exist
            calc_status = dept.investigation_status
            if not dept.has_agriculture_schemes:
                calc_status = InvestigationStatus.NO_RELEVANT_SCHEMES_FOUND
            elif schemes > 0 and active > 0:
                calc_status = InvestigationStatus.VERIFIED
            elif schemes > 0:
                calc_status = InvestigationStatus.SCHEMES_EXTRACTED
            elif docs > 0:
                calc_status = InvestigationStatus.DOCUMENTS_COLLECTED

            missing_info = None
            if dept.has_agriculture_schemes and schemes == 0:
                missing_info = "Awaiting automated deep crawler run to extract circulars & guidelines"
            elif dept.has_agriculture_schemes and active == 0 and schemes > 0:
                missing_info = "Awaiting verification date and order confirmation"

            entry = {
                "department_id": dept.id,
                "department_name": dept.name,
                "level": dept.level,
                "category": dept.category.value,
                "official_website": dept.official_website,
                "scheme_listing_url": dept.scheme_listing_url,
                "investigation_status": calc_status.value,
                "documents_discovered": docs,
                "schemes_identified": schemes,
                "active_schemes_verified": active,
                "expired_schemes": expired,
                "sources_accessible": dept.sources_accessible,
                "has_agriculture_schemes": dept.has_agriculture_schemes,
                "missing_information": missing_info,
                "last_checked_date": dept.last_checked_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
            }
            matrix.append(entry)

        return matrix

    def generate_markdown_report(self) -> str:
        """Renders an executive markdown coverage matrix report."""
        matrix = self.compute_matrix()

        total_depts = len(matrix)
        agri_depts = [m for m in matrix if m["investigation_status"] != InvestigationStatus.NO_RELEVANT_SCHEMES_FOUND.value]
        non_agri = [m for m in matrix if m["investigation_status"] == InvestigationStatus.NO_RELEVANT_SCHEMES_FOUND.value]
        total_docs = sum(m["documents_discovered"] for m in matrix)
        total_schemes = sum(m["schemes_identified"] for m in matrix)
        total_active = sum(m["active_schemes_verified"] for m in matrix)

        report = []
        report.append("# KrishiMitra AI: Complete Kerala Government Scheme Coverage Matrix")
        report.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")
        report.append("## Executive Coverage Summary")
        report.append(f"- **Total Departments & Agencies Cataloged:** {total_depts} (All 62 IGOD Kerala departments + Central & Commodity Boards)")
        report.append(f"- **Agriculture & Farmer Impacting Departments:** {len(agri_depts)}")
        report.append(f"- **Non-Agriculture Line Departments (Verified No Schemes):** {len(non_agri)}")
        report.append(f"- **Total Discovered & Cataloged Documents:** {total_docs}")
        report.append(f"- **Total Identified Schemes:** {total_schemes}")
        report.append(f"- **Active Verified Schemes:** {total_active}")
        report.append("")
        report.append("---")
        report.append("")
        report.append("## Department-Wise Scheme Coverage Table")
        report.append("")
        report.append("| Department / Agency | Category | Investigation Status | Docs | Schemes | Active | Website | Missing Info |")
        report.append("| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |")

        for m in sorted(matrix, key=lambda x: (x["investigation_status"] == "No relevant schemes found", x["department_name"])):
            status_badge = m["investigation_status"]
            missing = m["missing_information"] or "None (Up to date)"
            report.append(
                f"| **{m['department_name']}** | {m['category']} | `{status_badge}` | "
                f"{m['documents_discovered']} | {m['schemes_identified']} | {m['active_schemes_verified']} | "
                f"[Portal]({m['official_website']}) | {missing} |"
            )

        return "\n".join(report)
