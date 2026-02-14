from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Experiment, ExperimentResult
import json


@login_required
def experiment_list(request):
    """Experiment results explorer."""
    qs = ExperimentResult.objects.select_related(
        "experiment", "formulation", "formulation__ionizable_lipid"
    )

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(lnp_id__icontains=q) |
            Q(formulation__ionizable_lipid__name__icontains=q)
        )

    method = request.GET.get("method")
    if method:
        qs = qs.filter(method=method)

    cargo = request.GET.get("cargo")
    if cargo:
        qs = qs.filter(experiment__cargo=cargo)

    model_name = request.GET.get("model")
    if model_name:
        qs = qs.filter(experiment__model_name=model_name)

    total = qs.count()
    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page", 1))

    # Filter choices
    methods = ExperimentResult.Method.choices
    cargos = Experiment.CargoType.choices
    model_names = (
        Experiment.objects.values_list("model_name", flat=True)
        .distinct()
        .order_by("model_name")
    )
    # Method distribution for stats
    method_count = ExperimentResult.objects.values("method").annotate(c=Count("id")).count()

    ctx = {
        "page": page,
        "query": q,
        "methods": methods,
        "cargos": cargos,
        "model_names": model_names,
        "total": total,
        "method_count": method_count,
        "current_method": method or "",
        "current_cargo": cargo or "",
        "current_model": model_name or "",
    }
    if request.headers.get("HX-Request"):
        return render(request, "experiments/_table.html", ctx)
    return render(request, "experiments/list.html", ctx)
