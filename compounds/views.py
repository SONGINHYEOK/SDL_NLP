from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import IonizableLipid, HeadGroup, HelperLipid, Cholesterol, PEGLipid
from experiments.models import ExperimentResult
import json


@login_required
def lipid_list(request):
    """Lipid Explorer: search, filter, paginate ionizable lipids."""
    qs = IonizableLipid.objects.select_related("head_group", "linker", "tail1", "tail2")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(smiles__icontains=q))

    head = request.GET.get("head")
    if head:
        qs = qs.filter(head_group__name=head)

    struct = request.GET.get("struct")
    if struct == "ester":
        qs = qs.filter(has_ester=True)
    elif struct == "carbonate":
        qs = qs.filter(has_carbonate=True)
    elif struct == "disulfide":
        qs = qs.filter(has_disulfide=True)

    mw_min = request.GET.get("mw_min")
    mw_max = request.GET.get("mw_max")
    if mw_min:
        qs = qs.filter(molecular_weight__gte=float(mw_min))
    if mw_max:
        qs = qs.filter(molecular_weight__lte=float(mw_max))

    logp_min = request.GET.get("logp_min")
    logp_max = request.GET.get("logp_max")
    if logp_min:
        qs = qs.filter(logp__gte=float(logp_min))
    if logp_max:
        qs = qs.filter(logp__lte=float(logp_max))

    sort = request.GET.get("sort", "name")
    valid_sorts = ["name", "-name", "molecular_weight", "-molecular_weight", "logp", "-logp"]
    if sort in valid_sorts:
        qs = qs.order_by(sort)

    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page", 1))

    heads = HeadGroup.objects.annotate(lipid_count=Count("lipids")).order_by("-lipid_count")[:30]

    ctx = {
        "page": page,
        "query": q,
        "heads": heads,
        "current_head": head,
        "current_struct": struct,
        "sort": sort,
        "total_count": qs.count(),
    }
    if request.headers.get("HX-Request"):
        return render(request, "compounds/_lipid_table.html", ctx)
    return render(request, "compounds/list.html", ctx)


@login_required
def lipid_detail(request, pk):
    """Single lipid detail with descriptors, radar chart, structure, experiments."""
    lipid = get_object_or_404(
        IonizableLipid.objects.select_related("head_group", "linker", "tail1", "tail2"),
        pk=pk
    )

    # ── Experiment results for this lipid ──
    results = (
        ExperimentResult.objects
        .filter(formulation__ionizable_lipid=lipid)
        .select_related("experiment", "formulation")
        .order_by("-value")
    )
    total_results = results.count()
    results_page = results[:50]

    # Results by method
    method_summary = (
        results.values("method")
        .annotate(count=Count("id"), avg_val=Avg("value"))
        .order_by("-count")
    )

    # Results by cargo
    cargo_summary = (
        results.values("experiment__cargo")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Results by model
    model_summary = (
        results.values("experiment__model_name")
        .annotate(count=Count("id"), avg_val=Avg("value"))
        .order_by("-count")[:8]
    )

    # ── Descriptor radar chart data ──
    # This lipid's descriptors (normalized 0-1 against DB range)
    db_stats = IonizableLipid.objects.aggregate(
        mw_min=Avg("molecular_weight") * 0,  # placeholder
        mw_max=Avg("molecular_weight") * 2,
        mw_avg=Avg("molecular_weight"),
        logp_avg=Avg("logp"),
        tpsa_avg=Avg("tpsa"),
        hbd_avg=Avg("hbd"),
        hba_avg=Avg("hba"),
        rb_avg=Avg("rotatable_bonds"),
        rings_avg=Avg("rings"),
        fsp3_avg=Avg("fsp3"),
        mr_avg=Avg("molar_refractivity"),
        ha_avg=Avg("heavy_atoms"),
        nc_avg=Avg("nitrogen_count"),
    )

    # Normalization ranges from actual LNPDB
    ranges = {
        "MW": (200, 4000),
        "LogP": (-4, 80),
        "TPSA": (0, 200),
        "HBD": (0, 10),
        "HBA": (0, 30),
        "RotBonds": (0, 80),
        "Rings": (0, 10),
        "Fsp3": (0, 1),
        "MolarRef": (0, 1200),
        "HeavyAtoms": (0, 300),
        "N_Count": (0, 10),
    }

    def normalize(val, key):
        if val is None:
            return 0
        lo, hi = ranges.get(key, (0, 1))
        if hi == lo:
            return 0
        return max(0, min(1, (val - lo) / (hi - lo)))

    lipid_radar = {
        "MW": normalize(lipid.molecular_weight, "MW"),
        "LogP": normalize(lipid.logp, "LogP"),
        "TPSA": normalize(lipid.tpsa, "TPSA"),
        "HBD": normalize(lipid.hbd, "HBD"),
        "HBA": normalize(lipid.hba, "HBA"),
        "RotBonds": normalize(lipid.rotatable_bonds, "RotBonds"),
        "Rings": normalize(lipid.rings, "Rings"),
        "Fsp3": normalize(lipid.fsp3, "Fsp3"),
        "MolarRef": normalize(lipid.molar_refractivity, "MolarRef"),
        "HeavyAtoms": normalize(lipid.heavy_atoms, "HeavyAtoms"),
        "N_Count": normalize(lipid.nitrogen_count, "N_Count"),
    }

    avg_radar = {
        "MW": normalize(db_stats["mw_avg"], "MW"),
        "LogP": normalize(db_stats["logp_avg"], "LogP"),
        "TPSA": normalize(db_stats["tpsa_avg"], "TPSA"),
        "HBD": normalize(db_stats["hbd_avg"], "HBD"),
        "HBA": normalize(db_stats["hba_avg"], "HBA"),
        "RotBonds": normalize(db_stats["rb_avg"], "RotBonds"),
        "Rings": normalize(db_stats["rings_avg"], "Rings"),
        "Fsp3": normalize(db_stats["fsp3_avg"], "Fsp3"),
        "MolarRef": normalize(db_stats["mr_avg"], "MolarRef"),
        "HeavyAtoms": normalize(db_stats["ha_avg"], "HeavyAtoms"),
        "N_Count": normalize(db_stats["nc_avg"], "N_Count"),
    }

    # Value distribution for histogram
    lum_values = list(
        results.filter(method="luminescence_normalized")
        .values_list("value", flat=True)[:200]
    )

    # ── Navigation: prev/next lipid ──
    next_lipid = IonizableLipid.objects.filter(pk__gt=pk).order_by("pk").first()
    prev_lipid = IonizableLipid.objects.filter(pk__lt=pk).order_by("-pk").first()

    ctx = {
        "lipid": lipid,
        "results": results_page,
        "total_results": total_results,
        "method_summary": list(method_summary),
        "cargo_summary": list(cargo_summary),
        "model_summary": list(model_summary),
        "radar_labels_json": json.dumps(list(lipid_radar.keys())),
        "lipid_radar_json": json.dumps(list(lipid_radar.values())),
        "avg_radar_json": json.dumps(list(avg_radar.values())),
        "lum_values_json": json.dumps(lum_values),
        "next_lipid": next_lipid,
        "prev_lipid": prev_lipid,
    }
    return render(request, "compounds/detail.html", ctx)


@login_required
def lipid_compare(request):
    ids = request.GET.getlist("ids")
    lipids = list(
        IonizableLipid.objects.filter(pk__in=ids)
        .select_related("head_group", "linker", "tail1", "tail2")
    ) if ids else []

    # Normalization ranges (same as detail page)
    ranges = {
        "MW": (200, 4000), "LogP": (-4, 80), "TPSA": (0, 200),
        "HBD": (0, 10), "HBA": (0, 30), "RotBonds": (0, 80),
        "Rings": (0, 10), "Fsp3": (0, 1), "MolarRef": (0, 1200),
        "HeavyAtoms": (0, 300), "N_Count": (0, 10),
    }

    def normalize(val, key):
        if val is None:
            return 0
        lo, hi = ranges.get(key, (0, 1))
        return max(0, min(1, (val - lo) / (hi - lo))) if hi != lo else 0

    radar_labels = list(ranges.keys())
    radar_datasets = []
    for lip in lipids:
        vals = [
            normalize(lip.molecular_weight, "MW"),
            normalize(lip.logp, "LogP"),
            normalize(lip.tpsa, "TPSA"),
            normalize(lip.hbd, "HBD"),
            normalize(lip.hba, "HBA"),
            normalize(lip.rotatable_bonds, "RotBonds"),
            normalize(lip.rings, "Rings"),
            normalize(lip.fsp3, "Fsp3"),
            normalize(lip.molar_refractivity, "MolarRef"),
            normalize(lip.heavy_atoms, "HeavyAtoms"),
            normalize(lip.nitrogen_count, "N_Count"),
        ]
        radar_datasets.append({"id": lip.pk, "name": lip.name[:25], "values": vals})

    # DB average for reference
    db_stats = IonizableLipid.objects.aggregate(
        mw=Avg("molecular_weight"), lp=Avg("logp"), tp=Avg("tpsa"),
        hbd=Avg("hbd"), hba=Avg("hba"), rb=Avg("rotatable_bonds"),
        rings=Avg("rings"), fsp3=Avg("fsp3"), mr=Avg("molar_refractivity"),
        ha=Avg("heavy_atoms"), nc=Avg("nitrogen_count"),
    )
    avg_radar = [
        normalize(db_stats["mw"], "MW"), normalize(db_stats["lp"], "LogP"),
        normalize(db_stats["tp"], "TPSA"), normalize(db_stats["hbd"], "HBD"),
        normalize(db_stats["hba"], "HBA"), normalize(db_stats["rb"], "RotBonds"),
        normalize(db_stats["rings"], "Rings"), normalize(db_stats["fsp3"], "Fsp3"),
        normalize(db_stats["mr"], "MolarRef"), normalize(db_stats["ha"], "HeavyAtoms"),
        normalize(db_stats["nc"], "N_Count"),
    ]

    # Experiment stats per lipid
    exp_stats = []
    for lip in lipids:
        results = ExperimentResult.objects.filter(formulation__ionizable_lipid=lip)
        total = results.count()
        avg_val = results.aggregate(avg=Avg("value"))["avg"]
        exp_stats.append({"id": lip.pk, "total": total, "avg": round(avg_val or 0, 4)})

    ctx = {
        "lipids": lipids,
        "radar_labels_json": json.dumps(radar_labels),
        "radar_datasets_json": json.dumps(radar_datasets),
        "avg_radar_json": json.dumps(avg_radar),
        "exp_stats_json": json.dumps(exp_stats),
    }
    return render(request, "compounds/compare.html", ctx)


@login_required
def helper_lipids(request):
    ctx = {
        "helpers": HelperLipid.objects.annotate(usage=Count("formulations")),
        "cholesterols": Cholesterol.objects.annotate(usage=Count("formulations")),
        "pegs": PEGLipid.objects.annotate(usage=Count("formulations")),
    }
    return render(request, "compounds/helpers.html", ctx)
