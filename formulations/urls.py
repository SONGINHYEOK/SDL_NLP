from django.urls import path
from . import views

app_name = "formulations"
urlpatterns = [
    path("", views.formulation_list, name="list"),
    path("designer/", views.formulation_designer, name="designer"),
    path("api/search-lipids/", views.search_lipids_api, name="search_lipids"),
    path("api/similar/", views.similar_formulations_api, name="similar"),
]
