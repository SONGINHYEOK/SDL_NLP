from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Equipment, EquipmentStatus, MaintenanceRecord


@login_required
def monitor(request):
    """Equipment monitoring dashboard."""
    equipment = Equipment.objects.prefetch_related("status_logs").all()
    eq_with_status = []
    for eq in equipment:
        latest = eq.status_logs.first()
        eq_with_status.append({"equipment": eq, "latest_status": latest})
    ctx = {"equipment_list": eq_with_status}
    return render(request, "equipment/monitor.html", ctx)


@login_required
def maintenance(request):
    """Equipment maintenance dashboard."""
    today = timezone.now().date()

    overdue = MaintenanceRecord.objects.filter(
        status__in=["scheduled", "overdue"],
        scheduled_date__lt=today,
    ).select_related("equipment")
    # Auto-mark overdue
    overdue.filter(status="scheduled").update(status="overdue")

    upcoming = (
        MaintenanceRecord.objects
        .filter(status__in=["scheduled", "in_progress"])
        .select_related("equipment")
        .order_by("scheduled_date")[:10]
    )

    completed = (
        MaintenanceRecord.objects
        .filter(status="completed")
        .select_related("equipment", "performed_by")
        .order_by("-completed_date")[:10]
    )

    ctx = {
        "overdue": overdue,
        "upcoming": upcoming,
        "completed": completed,
        "overdue_count": overdue.count(),
        "upcoming_count": upcoming.count(),
        "completed_count": completed.count(),
    }
    return render(request, "equipment/maintenance.html", ctx)
