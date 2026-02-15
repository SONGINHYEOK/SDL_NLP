from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("dashboard.urls")),
    path("compounds/", include("compounds.urls")),
    path("formulations/", include("formulations.urls")),
    path("experiments/", include("experiments.urls")),
    path("ai/", include("ai_models.urls")),
    path("equipment/", include("equipment.urls")),
    path("inventory/", include("inventory.urls")),
    path("workflow/", include("workflow.urls")),
    # DRF API
    path("api/equipment/", include("equipment.api_urls")),
    # AI Assistant
    path("assistant/", include("assistant.urls")),
]
