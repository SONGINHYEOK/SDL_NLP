from django.contrib import admin
from .models import Experiment, ExperimentResult

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ["experiment_id", "model_name", "model_type", "cargo", "route"]
    list_filter = ["model_type", "cargo", "route"]

@admin.register(ExperimentResult)
class ExperimentResultAdmin(admin.ModelAdmin):
    list_display = ["lnp_id", "method", "value"]
    list_filter = ["method"]
    search_fields = ["lnp_id"]
    raw_id_fields = ["experiment", "formulation"]
