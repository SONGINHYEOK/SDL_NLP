from django.contrib import admin
from .models import Reagent, ReagentStock, ReagentConsumption


@admin.register(Reagent)
class ReagentAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "unit", "minimum_stock", "current_stock", "stock_status"]
    list_filter = ["category"]
    search_fields = ["name", "cas_number"]


@admin.register(ReagentStock)
class ReagentStockAdmin(admin.ModelAdmin):
    list_display = ["reagent", "lot_number", "quantity", "initial_quantity", "location", "expiry_date", "is_active"]
    list_filter = ["is_active", "reagent__category"]
    search_fields = ["lot_number", "reagent__name"]


@admin.register(ReagentConsumption)
class ReagentConsumptionAdmin(admin.ModelAdmin):
    list_display = ["reagent", "quantity_used", "batch_id", "workflow_step", "timestamp"]
    list_filter = ["reagent"]
    search_fields = ["batch_id"]
