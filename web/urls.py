"""
URL Configuration for KrishiMitra AI Web Application.
"""

from django.urls import path
from web import views

urlpatterns = [
    # Farmer Portal
    path("", views.farmer_portal_view, name="farmer_portal"),
    path("farmer/", views.farmer_portal_view, name="farmer_portal_alt"),

    # Admin Dashboard
    path("admin-portal/", views.admin_dashboard_view, name="admin_dashboard"),

    # REST APIs
    path("api/coverage/matrix/", views.api_coverage_matrix, name="api_coverage_matrix"),
    path("api/schemes/", views.api_schemes_list, name="api_schemes_list"),
    path("api/schemes/<str:scheme_id>/", views.api_scheme_detail, name="api_scheme_detail"),
    path("api/eligibility/evaluate/", views.api_evaluate_eligibility, name="api_evaluate_eligibility"),
    path("api/chat/ask/", views.api_chat_ask, name="api_chat_ask"),
    path("api/admin/metrics/", views.api_admin_metrics, name="api_admin_metrics"),
    path("api/admin/schemes/<str:scheme_id>/verify/", views.api_admin_verify_scheme, name="api_admin_verify_scheme"),
    path("api/admin/crawl/trigger/", views.api_admin_trigger_crawl, name="api_admin_trigger_crawl"),
]
