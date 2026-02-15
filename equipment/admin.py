from django.contrib import admin
from .models import Equipment, EquipmentStatus, MaintenanceRecord

admin.site.register(Equipment)
admin.site.register(EquipmentStatus)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ["equipment", "maintenance_type", "status", "scheduled_date", "completed_date", "next_due_date"]
    list_filter = ["status", "maintenance_type"]
    search_fields = ["equipment__name", "description"]
