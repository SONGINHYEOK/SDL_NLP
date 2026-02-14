from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from .models import LNPFormulation
import json


@login_required
def formulation_list(request):
    """Formulation list with search and filter."""
    qs = LNPFormulation.objects.select_related(
        "ionizable_lipid", "helper_lipid", "cholesterol", "peg_lipid"
    ).annotate(result_count=Count("results"))

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(formulation_id__icontains=q) |
            Q(ionizable_lipid__name__icontains=q)
        )

    mixing = request.GET.get("mixing")
    if mixing:
        qs = qs.filter(mixing_method=mixing)

    cargo = request.GET.get("cargo")
    if cargo:
        qs = qs.filter(results__experiment__cargo=cargo).distinct()

    sort = request.GET.get("sort", "-result_count")
    qs = qs.order_by(sort)

    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page", 1))

    ctx = {"page": page, "query": q, "total": qs.count(), "sort": sort}
    if request.headers.get("HX-Request"):
        return render(request, "formulations/_table.html", ctx)
    return render(request, "formulations/list.html", ctx)


@login_required
def formulation_designer(request):
    """Interactive formulation designer with composition sliders + AI prediction."""
    from compounds.models import IonizableLipid, HelperLipid, Cholesterol, PEGLipid

    # Top lipids for quick selection
    top_lipids = (
        IonizableLipid.objects
        .annotate(usage=Count("formulations"))
        .order_by("-usage")[:20]
    )

    ctx = {
        "helpers": list(HelperLipid.objects.annotate(usage=Count("formulations")).order_by("-usage").values("pk", "name", "usage")),
        "cholesterols": list(Cholesterol.objects.annotate(usage=Count("formulations")).order_by("-usage").values("pk", "name", "usage")),
        "pegs": list(PEGLipid.objects.annotate(usage=Count("formulations")).order_by("-usage").values("pk", "name", "usage")),
        "top_lipids": list(top_lipids.values("pk", "name", "molecular_weight", "logp", "has_ester", "has_carbonate", "has_disulfide", "usage")),
        "helpers_json": json.dumps(list(HelperLipid.objects.annotate(usage=Count("formulations")).order_by("-usage").values("pk", "name", "usage"))),
        "cholesterols_json": json.dumps(list(Cholesterol.objects.annotate(usage=Count("formulations")).order_by("-usage").values("pk", "name", "usage"))),
        "pegs_json": json.dumps(list(PEGLipid.objects.annotate(usage=Count("formulations")).order_by("-usage").values("pk", "name", "usage"))),
    }
    return render(request, "formulations/designer.html", ctx)


def search_lipids_api(request):
    """HTMX/JSON endpoint: search ionizable lipids by name."""
    from compounds.models import IonizableLipid
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"results": []})

    qs = IonizableLipid.objects.filter(
        Q(name__icontains=q) | Q(smiles__icontains=q)
    ).order_by("name")[:15]

    results = [{
        "pk": il.pk,
        "name": il.name,
        "mw": il.molecular_weight,
        "logp": il.logp,
        "smiles": il.smiles[:60],
        "ester": il.has_ester,
        "carbonate": il.has_carbonate,
        "disulfide": il.has_disulfide,
    } for il in qs]

    return JsonResponse({"results": results})


def similar_formulations_api(request):
    """Find similar formulations in DB given composition parameters."""
    il_pk = request.GET.get("il_pk")
    hl_name = request.GET.get("hl")
    il_ratio = float(request.GET.get("il_ratio", 50))

    qs = LNPFormulation.objects.select_related(
        "ionizable_lipid", "helper_lipid", "cholesterol", "peg_lipid"
    )

    if il_pk:
        qs = qs.filter(ionizable_lipid_id=il_pk)
    # Try with HL filter first, fallback without
    if hl_name:
        qs_hl = qs.filter(helper_lipid__name=hl_name)
        if qs_hl.exists():
            qs = qs_hl

    # Sort by closest IL ratio
    results = []
    for f in qs[:20]:
        diff = abs((f.il_molratio or 0) - il_ratio)
        avg_val = f.results.aggregate(avg=Avg("value"))["avg"]
        results.append({
            "id": f.formulation_id,
            "il": f.ionizable_lipid.name[:25],
            "hl": f.helper_lipid.name if f.helper_lipid else "-",
            "ratio": f"{f.il_molratio or 0:.0f}:{f.hl_molratio or 0:.0f}:{f.chl_molratio or 0:.0f}:{f.peg_molratio or 0:.0f}",
            "mixing": f.mixing_method,
            "np": f.il_to_na_chargeratio,
            "avg_value": round(avg_val, 4) if avg_val else None,
            "diff": round(diff, 1),
        })

    results.sort(key=lambda x: x["diff"])
    return JsonResponse({"results": results[:10]})
