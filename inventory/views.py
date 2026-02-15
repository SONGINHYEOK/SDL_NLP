from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Reagent, ReagentConsumption


@login_required
def dashboard(request):
    """Inventory dashboard: stats, alerts, stock table, consumption timeline."""
    reagents = Reagent.objects.prefetch_related("stocks").all()

    # Build reagent list with computed fields
    reagent_list = []
    low_stock = []
    categories = set()
    for r in reagents:
        categories.add(r.category)
        stock = r.current_stock
        status = r.stock_status
        reagent_list.append({
            "id": r.pk,
            "name": r.name,
            "category": r.category,
            "category_display": r.get_category_display(),
            "unit": r.get_unit_display(),
            "current_stock": stock,
            "minimum_stock": r.minimum_stock,
            "stock_status": status,
            "stock_pct": min(100, round(stock / r.minimum_stock * 100, 1)) if r.minimum_stock > 0 else 100,
            "storage": r.storage_conditions,
        })
        if status in ("critical", "warning"):
            low_stock.append(reagent_list[-1])

    # Recent consumptions
    recent_consumptions = (
        ReagentConsumption.objects
        .select_related("reagent", "stock_lot", "workflow_step", "workflow_step__workflow")
        .order_by("-timestamp")[:20]
    )

    ctx = {
        "total_reagents": len(reagent_list),
        "low_stock_count": len(low_stock),
        "recent_consumption_count": ReagentConsumption.objects.count(),
        "category_count": len(categories),
        "low_stock": low_stock,
        "reagent_list": reagent_list,
        "recent_consumptions": recent_consumptions,
    }
    return render(request, "inventory/dashboard.html", ctx)
