"""
Views and API Endpoints for KrishiMitra AI Web Platform.
Serves Farmer Portal, Admin Dashboard, and REST APIs.
"""

import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from registry.source_registry import SourceRegistry
from registry.coverage_matrix import SchemeCoverageMatrix
from crawler.discovery_engine import DiscoveryEngine
from eligibility.models import FarmerInputProfile
from eligibility.checker import EligibilityChecker
from rag.assistant import FarmerAssistant
from core.database import get_connection
from core.logger import get_logger

logger = get_logger("krishimitra.web.views")

# Global singletons
registry = SourceRegistry()
coverage_engine = SchemeCoverageMatrix(registry)
eligibility_checker = EligibilityChecker()
assistant = FarmerAssistant()
discovery_engine = DiscoveryEngine(registry)

def farmer_portal_view(request):
    """Renders the mobile-first, accessible Farmer Portal."""
    return render(request, "farmer.html")

def admin_dashboard_view(request):
    """Renders the comprehensive KrishiMitra Admin Dashboard."""
    return render(request, "admin.html")

def api_coverage_matrix(request):
    """Returns the live 62 department Scheme Coverage Matrix."""
    matrix = coverage_engine.compute_matrix()
    return JsonResponse({"status": "success", "total_departments": len(matrix), "matrix": matrix})

def api_schemes_list(request):
    """Returns searchable schemes with district and crop filters in a single efficient query."""
    crop = request.GET.get("crop", "").strip().lower()
    district = request.GET.get("district", "").strip().lower()
    status = request.GET.get("status", "").strip().upper()

    schemes = []
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        s.id, s.name, s.malayalam_name, s.classification, s.status, s.level,
                        s.official_portal_url, s.last_verified_at,
                        d.name as dept_name,
                        b.subsidy_percentage, b.subsidy_amount, b.max_assistance_limit,
                        COALESCE(ARRAY_AGG(DISTINCT sc.crop_name) FILTER (WHERE sc.crop_name IS NOT NULL), '{}') as crops
                    FROM schemes s
                    LEFT JOIN government_departments d ON s.department_id = d.id
                    LEFT JOIN scheme_benefits b ON s.id = b.scheme_id
                    LEFT JOIN scheme_crops sc ON s.id = sc.scheme_id
                    GROUP BY s.id, s.name, s.malayalam_name, s.classification, s.status, s.level,
                             s.official_portal_url, s.last_verified_at, d.name,
                             b.subsidy_percentage, b.subsidy_amount, b.max_assistance_limit
                    ORDER BY s.created_at DESC;
                    """
                )
                rows = cur.fetchall()

                for r in rows:
                    crops = r["crops"] or []
                    if crop and not any(crop in c.lower() for c in crops):
                        continue
                    if status and r["status"] != status:
                        continue

                    b_str = "Scale of finance"
                    if r["subsidy_percentage"]:
                        b_str = f"{r['subsidy_percentage']}% subsidy"
                    elif r["subsidy_amount"]:
                        b_str = f"Rs {r['subsidy_amount']}"
                    if r["max_assistance_limit"]:
                        b_str += f" (Max Rs {r['max_assistance_limit']})"

                    schemes.append({
                        "id": r["id"],
                        "name": r["name"],
                        "malayalam_name": r["malayalam_name"],
                        "department": r["dept_name"],
                        "classification": r["classification"],
                        "status": r["status"],
                        "level": r["level"],
                        "benefits_summary": b_str,
                        "portal_url": r["official_portal_url"],
                        "crops": crops,
                        "last_verified": str(r["last_verified_at"] or "")
                    })
    except Exception as e:
        logger.error(f"Error fetching schemes list: {e}")

    return JsonResponse({"status": "success", "count": len(schemes), "schemes": schemes})

def api_scheme_detail(request, scheme_id):
    """Returns complete details of a single scheme."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT s.*, d.name as dept_name FROM schemes s LEFT JOIN government_departments d ON s.department_id = d.id WHERE s.id = %s;", (scheme_id,))
                scheme = cur.fetchone()
                if not scheme:
                    return JsonResponse({"status": "error", "message": "Scheme not found"}, status=404)

                cur.execute("SELECT * FROM scheme_benefits WHERE scheme_id = %s;", (scheme_id,))
                benefits = cur.fetchall()
                cur.execute("SELECT * FROM scheme_eligibility WHERE scheme_id = %s;", (scheme_id,))
                eligibility = cur.fetchall()
                cur.execute("SELECT crop_name FROM scheme_crops WHERE scheme_id = %s;", (scheme_id,))
                crops = [c["crop_name"] for c in cur.fetchall()]
                cur.execute("SELECT district_name FROM scheme_districts WHERE scheme_id = %s;", (scheme_id,))
                districts = [d["district_name"] for d in cur.fetchall()]
                cur.execute("SELECT document_name, is_mandatory FROM application_guidelines WHERE scheme_id = %s;", (scheme_id,))
                guidelines = cur.fetchall()

                return JsonResponse({
                    "status": "success",
                    "scheme": dict(scheme),
                    "benefits": [dict(b) for b in benefits],
                    "eligibility": [dict(e) for e in eligibility],
                    "crops": crops,
                    "districts": districts,
                    "documents_checklist": [dict(g) for g in guidelines]
                })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def api_evaluate_eligibility(request):
    """Evaluates farmer input profile against all schemes."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        profile = FarmerInputProfile(
            full_name=data.get("full_name", "Kerala Farmer"),
            district=data.get("district", "Palakkad"),
            farmer_type=data.get("farmer_type", "Small Farmer"),
            total_land_acres=float(data.get("total_land_acres", 1.5)),
            primary_crops=data.get("primary_crops", ["Paddy"]),
            annual_income=float(data.get("annual_income", 150000.0)),
            irrigation_type=data.get("irrigation_type", "Rainfed"),
            caste_category=data.get("caste_category", "General")
        )
        result = eligibility_checker.evaluate_farmer(profile)
        return JsonResponse({"status": "success", "result": result.model_dump()})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@csrf_exempt
def api_chat_ask(request):
    """Handles questions submitted to the RAG AI Farmer Assistant."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()
        language = data.get("language", "en")
        if not query:
            return JsonResponse({"status": "error", "message": "Query cannot be empty"}, status=400)

        res = assistant.answer_question(query, language=language)
        return JsonResponse({"status": "success", "response": res})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def api_admin_metrics(request):
    """Returns overview KPI metrics for the Admin Dashboard."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) as total FROM scheme_documents;")
                total_docs = cur.fetchone()["total"]
                cur.execute("SELECT count(*) as total FROM scheme_documents WHERE processing_status = 'PROCESSED';")
                processed_docs = cur.fetchone()["total"]
                cur.execute("SELECT count(*) as total FROM schemes;")
                total_schemes = cur.fetchone()["total"]
                cur.execute("SELECT count(*) as total FROM schemes WHERE status = 'ACTIVE' OR is_active = TRUE;")
                active_schemes = cur.fetchone()["total"]
                cur.execute("SELECT count(*) as total FROM schemes WHERE status = 'VERIFICATION_PENDING';")
                pending_verification = cur.fetchone()["total"]
                cur.execute("SELECT count(*) as total FROM schemes WHERE status = 'EXPIRED';")
                expired_schemes = cur.fetchone()["total"]

                # Recent documents
                cur.execute("SELECT title, original_url, doc_type, processing_status, created_at FROM scheme_documents ORDER BY created_at DESC LIMIT 5;")
                recent_docs = [dict(r) for r in cur.fetchall()]

                return JsonResponse({
                    "status": "success",
                    "metrics": {
                        "total_documents": total_docs,
                        "processed_documents": processed_docs,
                        "total_schemes": total_schemes,
                        "active_schemes": active_schemes,
                        "pending_verification": pending_verification,
                        "expired_schemes": expired_schemes
                    },
                    "recent_documents": recent_docs
                })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def api_admin_verify_scheme(request, scheme_id):
    """Admin endpoint to approve, reject, or update scheme status."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        action = data.get("action", "APPROVE").upper() # APPROVE, REJECT, MARK_INACTIVE

        new_status = "ACTIVE" if action == "APPROVE" else ("REJECTED" if action == "REJECT" else "EXPIRED")
        is_active = (new_status == "ACTIVE")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE schemes
                    SET status = %s, is_active = %s, last_verified_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (new_status, is_active, scheme_id)
                )
                cur.execute(
                    """
                    INSERT INTO verification_history (scheme_id, verified_by, action, new_status, reason)
                    VALUES (%s, 'Admin-Manual', %s, %s, %s);
                    """,
                    (scheme_id, action, new_status, data.get("reason", "Admin verification review"))
                )
            conn.commit()

        return JsonResponse({"status": "success", "message": f"Scheme {scheme_id} updated to {new_status}"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def api_admin_trigger_crawl(request):
    """Triggers manual crawler for a chosen department."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        dept_id = data.get("department_id", "KL_AGRI_DEPT")
        discovered = discovery_engine.run_department_crawl(dept_id)
        return JsonResponse({"status": "success", "department_id": dept_id, "discovered_count": len(discovered)})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
