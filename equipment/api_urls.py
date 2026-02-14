from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import EquipmentViewSet, EquipmentStatusViewSet

router = DefaultRouter()
router.register(r"devices", EquipmentViewSet)
router.register(r"status", EquipmentStatusViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
