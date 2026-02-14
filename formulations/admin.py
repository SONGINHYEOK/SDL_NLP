from django.contrib import admin
from .models import LNPFormulation

@admin.register(LNPFormulation)
class LNPFormulationAdmin(admin.ModelAdmin):
    list_display = ["formulation_id", "ionizable_lipid", "il_molratio", "mixing_method", "source"]
    list_filter = ["mixing_method", "source"]
    search_fields = ["formulation_id"]
    raw_id_fields = ["ionizable_lipid"]
