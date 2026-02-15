from django.urls import path
from . import views

app_name = "equipment"
urlpatterns = [
    path("", views.monitor, name="monitor"),
    path("maintenance/", views.maintenance, name="maintenance"),
]
