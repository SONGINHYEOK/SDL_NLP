from django.urls import path
from . import views

app_name = "ai_models"
urlpatterns = [
    path("predict/", views.predict, name="predict"),
    path("predict/api/", views.predict_api, name="predict_api"),
    path("generate/", views.generate, name="generate"),
    path("generate/api/", views.generate_api, name="generate_api"),
    path("optimize/", views.optimize, name="optimize"),
]
