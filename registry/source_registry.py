"""
Source Registry Engine for KrishiMitra AI.
Manages department registrations, official sources, and syncing with PostgreSQL.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import json
from registry.models import GovernmentDepartmentModel, InvestigationStatus, DepartmentCategory
from registry.departments_data import DEPARTMENTS_REGISTRY
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.registry")

class SourceRegistry:
    def __init__(self):
        self.departments: Dict[str, GovernmentDepartmentModel] = {}
        self._load_initial_catalog()

    def _load_initial_catalog(self):
        """Loads departments and agencies into memory models."""
        for item in DEPARTMENTS_REGISTRY:
            model = GovernmentDepartmentModel(
                id=item["id"],
                name=item["name"],
                malayalam_name=item.get("malayalam_name"),
                level=item.get("level", "State"),
                category=item["category"],
                official_website=item["official_website"],
                scheme_listing_url=item.get("scheme_listing_url"),
                portal_type=item.get("portal_type", "Department"),
                has_agriculture_schemes=item.get("has_agriculture_schemes", True),
                investigation_status=item.get("investigation_status", InvestigationStatus.NOT_INVESTIGATED),
                notes=item.get("notes")
            )
            self.departments[model.id] = model
        logger.info(f"Loaded {len(self.departments)} departments and agencies into SourceRegistry.")

    def sync_to_database(self) -> int:
        """Syncs all in-memory departments and sources to PostgreSQL."""
        logger.info("Syncing departments catalog to PostgreSQL database...")
        synced_count = 0
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for dept in self.departments.values():
                        cur.execute(
                            """
                            INSERT INTO government_departments (
                                id, name, malayalam_name, level, category, official_website,
                                portal_type, investigation_status, has_agriculture_schemes, notes, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                            ON CONFLICT (id) DO UPDATE SET
                                name = EXCLUDED.name,
                                malayalam_name = EXCLUDED.malayalam_name,
                                official_website = EXCLUDED.official_website,
                                investigation_status = EXCLUDED.investigation_status,
                                has_agriculture_schemes = EXCLUDED.has_agriculture_schemes,
                                notes = EXCLUDED.notes,
                                updated_at = CURRENT_TIMESTAMP;
                            """,
                            (
                                dept.id, dept.name, dept.malayalam_name, dept.level, dept.category.value,
                                dept.official_website, dept.portal_type, dept.investigation_status.value,
                                dept.has_agriculture_schemes, dept.notes
                            )
                        )

                        # Also register primary source
                        source_id = f"SRC_{dept.id}"
                        cur.execute(
                            """
                            INSERT INTO government_sources (
                                id, department_id, name, base_url, scheme_listing_url, source_type, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                            ON CONFLICT (id) DO UPDATE SET
                                base_url = EXCLUDED.base_url,
                                scheme_listing_url = EXCLUDED.scheme_listing_url,
                                updated_at = CURRENT_TIMESTAMP;
                            """,
                            (
                                source_id, dept.id, f"{dept.name} Official Portal",
                                dept.official_website, dept.scheme_listing_url, dept.portal_type
                            )
                        )
                        synced_count += 1
                conn.commit()
            logger.info(f"Successfully synced {synced_count} departments and sources to PostgreSQL.")
            return synced_count
        except Exception as e:
            logger.error(f"Error syncing to database: {e}")
            raise e

    def get_agriculture_departments(self) -> List[GovernmentDepartmentModel]:
        """Returns all departments flagged as having agricultural or farmer schemes."""
        return [d for d in self.departments.values() if d.has_agriculture_schemes]

    def get_department(self, dept_id: str) -> Optional[GovernmentDepartmentModel]:
        return self.departments.get(dept_id)

    def update_status(self, dept_id: str, status: InvestigationStatus, notes: Optional[str] = None):
        if dept_id in self.departments:
            self.departments[dept_id].investigation_status = status
            if notes:
                self.departments[dept_id].notes = notes
            self.departments[dept_id].last_checked_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
