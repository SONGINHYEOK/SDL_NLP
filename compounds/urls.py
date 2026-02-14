from django.urls import path
from . import views

app_name = "compounds"
urlpatterns = [
    path("", views.lipid_list, name="list"),
    path("<int:pk>/", views.lipid_detail, name="detail"),
    path("compare/", views.lipid_compare, name="compare"),
    path("helpers/", views.helper_lipids, name="helpers"),
]
