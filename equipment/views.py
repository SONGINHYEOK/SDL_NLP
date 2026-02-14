from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Equipment, EquipmentStatus


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
