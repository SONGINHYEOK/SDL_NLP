from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Min, Max
from compounds.models import IonizableLipid, HelperLipid, Cholesterol, PEGLipid, HeadGroup
from formulations.models import LNPFormulation
from experiments.models import Experiment, ExperimentResult
from ai_models.models import AIModel, GeneratedCandidate, Prediction
from equipment.models import Equipment, EquipmentStatus
from workflow.models import WorkflowRun, WorkflowStep
import json


@login_required
def index(request):
    """Main dashboard with LNPDB statistics."""
    ctx = {}

    # Core stats
    ctx["total_results"] = ExperimentResult.objects.count()
    ctx["total_lipids"] = IonizableLipid.objects.count()
    ctx["total_heads"] = HeadGroup.objects.count()
    ctx["total_formulations"] = LNPFormulation.objects.count()
    ctx["total_experiments"] = Experiment.objects.count()

    # AI stats
    ctx["active_models"] = AIModel.objects.filter(is_active=True).count()
    ctx["total_models"] = AIModel.objects.count()
    ctx["total_candidates"] = GeneratedCandidate.objects.count()

    # Equipment stats
    ctx["total_equipment"] = Equipment.objects.count()
    ctx["online_equipment"] = Equipment.objects.filter(is_connected=True).count()
    ctx["equipment_list"] = Equipment.objects.all()[:6]

    # Workflow stats
    ctx["total_workflows"] = WorkflowRun.objects.count()
    ctx["running_workflows"] = WorkflowRun.objects.filter(status="running").count()

    # Charts: Cargo distribution
    cargo_dist = (
        Experiment.objects.values("cargo")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    ctx["cargo_dist_json"] = json.dumps(
        {r["cargo"]: r["count"] for r in cargo_dist}
    )

    # Charts: Model distribution (top 8)
    model_dist = (
        Experiment.objects.exclude(model_name="")
        .values("model_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:8]
    )
    ctx["model_dist"] = list(model_dist)

    # Charts: Method distribution
    method_dist = (
        ExperimentResult.objects.values("method")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    ctx["method_dist_json"] = json.dumps(
        {r["method"]: r["count"] for r in method_dist}
    )

    # Charts: Helper lipid distribution
    hl_dist = (
        LNPFormulation.objects.exclude(helper_lipid=None)
        .values("helper_lipid__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    ctx["hl_dist_json"] = json.dumps(
        {r["helper_lipid__name"]: r["count"] for r in hl_dist}
    )

    # MW stats
    mw_stats = IonizableLipid.objects.aggregate(
        avg=Avg("molecular_weight"), mn=Min("molecular_weight"), mx=Max("molecular_weight")
    )
    ctx["mw_avg"] = round(mw_stats["avg"] or 0, 1)
    ctx["mw_min"] = round(mw_stats["mn"] or 0, 1)
    ctx["mw_max"] = round(mw_stats["mx"] or 0, 1)

    # Top studied lipids
    top_lipids = (
        ExperimentResult.objects
        .values("formulation__ionizable_lipid__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:7]
    )
    ctx["top_lipids"] = list(top_lipids)

    # Recent results sample
    ctx["recent_results"] = (
        ExperimentResult.objects
        .select_related("experiment", "formulation", "formulation__ionizable_lipid")
        .order_by("lnp_id")[:20]
    )

    # ── P2 Widgets ──

    # Equipment status widget: latest status per device
    equip_statuses = []
    for eq in Equipment.objects.all()[:5]:
        latest = eq.status_logs.first()  # ordered by -timestamp
        equip_statuses.append({
            "name": eq.name,
            "type": eq.get_equipment_type_display(),
            "protocol": eq.get_protocol_display(),
            "connected": eq.is_connected,
            "status": latest.status if latest else "offline",
            "message": latest.message if latest else "",
        })
    ctx["equip_statuses"] = equip_statuses

    # Active workflow runs with steps
    active_runs = []
    for run in WorkflowRun.objects.prefetch_related("steps")[:3]:
        steps = []
        for s in run.steps.all():
            steps.append({
                "type": s.get_step_type_display(),
                "status": s.status,
            })
        active_runs.append({
            "pk": run.pk,
            "name": run.name,
            "status": run.status,
            "iteration": run.iteration,
            "progress": run.progress_pct,
            "steps": steps,
        })
    ctx["active_runs"] = active_runs

    # Inventory alerts
    try:
        from inventory.models import Reagent
        inventory_alerts = []
        for r in Reagent.objects.prefetch_related("stocks").all():
            status = r.stock_status
            if status in ("critical", "warning"):
                inventory_alerts.append({
                    "name": r.name,
                    "status": status,
                    "current": r.current_stock,
                    "minimum": r.minimum_stock,
                    "unit": r.get_unit_display(),
                })
        ctx["inventory_alerts"] = inventory_alerts
    except ImportError:
        ctx["inventory_alerts"] = []

    # AI models summary
    ai_models = []
    for m in AIModel.objects.all()[:4]:
        ai_models.append({
            "name": m.name,
            "type": m.get_model_type_display(),
            "version": m.version,
            "active": m.is_active,
            "metrics": m.metrics,
            "predictions": m.predictions.count(),
        })
    ctx["ai_models_summary"] = ai_models

    return render(request, "dashboard/index.html", ctx)
