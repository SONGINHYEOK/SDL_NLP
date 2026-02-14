from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg
from .models import AIModel, Prediction, GeneratedCandidate
from compounds.models import IonizableLipid
from formulations.models import LNPFormulation
from experiments.models import ExperimentResult
import json
import random


@login_required
def predict(request):
    """AI property prediction interface."""
    models = AIModel.objects.filter(model_type="property_predictor", is_active=True)
    recent_preds = Prediction.objects.select_related("ai_model")[:20]
    ctx = {"models": models, "recent_predictions": recent_preds}
    return render(request, "ai_models/predict.html", ctx)


def predict_api(request):
    """HTMX endpoint: run prediction on given SMILES or formulation."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    smiles = request.POST.get("smiles", "")
    if not smiles:
        return JsonResponse({"error": "SMILES required"}, status=400)

    # Demo: find closest lipid in DB and return its properties
    lipid = IonizableLipid.objects.filter(smiles=smiles).first()
    if lipid:
        result = lipid.descriptor_dict
        result["source"] = "database_match"
    else:
        # Placeholder: return average properties as "prediction"
        avgs = IonizableLipid.objects.aggregate(
            mw=Avg("molecular_weight"), lp=Avg("logp"), tp=Avg("tpsa"),
        )
        result = {
            "molecular_weight": round(avgs["mw"] or 0, 1),
            "logp": round(avgs["lp"] or 0, 1),
            "tpsa": round(avgs["tp"] or 0, 1),
            "source": "model_prediction",
            "confidence": 0.72,
            "note": "Demo prediction - replace with trained model",
        }

    return JsonResponse(result)


@login_required
def generate(request):
    """AI structure generation interface."""
    candidates = GeneratedCandidate.objects.select_related("ai_model").order_by("-created_at")[:50]
    generator_models = AIModel.objects.filter(model_type="structure_generator")
    ctx = {"candidates": candidates, "generator_models": generator_models}
    return render(request, "ai_models/generate.html", ctx)


def generate_api(request):
    """Demo: generate lipid candidates by sampling from DB."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    count = int(request.POST.get("count", 5))
    mw_min = float(request.POST.get("mw_min", 400))
    mw_max = float(request.POST.get("mw_max", 1500))
    logp_min = float(request.POST.get("logp_min", 5))
    logp_max = float(request.POST.get("logp_max", 30))

    qs = IonizableLipid.objects.filter(
        molecular_weight__gte=mw_min, molecular_weight__lte=mw_max,
        logp__gte=logp_min, logp__lte=logp_max,
    )
    total = qs.count()
    if total == 0:
        return JsonResponse({"candidates": [], "note": "No matching lipids in DB"})

    sample_ids = random.sample(list(qs.values_list("pk", flat=True)[:200]), min(count, total, 200))
    lipids = IonizableLipid.objects.filter(pk__in=sample_ids)

    candidates = []
    for i, lip in enumerate(lipids):
        candidates.append({
            "smiles": lip.smiles,
            "name": lip.name,
            "mw": lip.molecular_weight,
            "logp": lip.logp,
            "tpsa": lip.tpsa,
            "efficacy": round(random.uniform(0.4, 0.95), 3),
            "stability": round(random.uniform(0.5, 0.98), 3),
            "safety": round(random.uniform(0.6, 0.99), 3),
            "pareto_rank": i + 1,
        })
    candidates.sort(key=lambda c: -c["efficacy"])
    for i, c in enumerate(candidates):
        c["pareto_rank"] = i + 1

    return JsonResponse({"candidates": candidates, "source": "demo_sampler"})


@login_required
def optimize(request):
    """Multi-objective optimization with ternary plot."""
    # Get formulation data for ternary diagram
    formulations = (
        LNPFormulation.objects.filter(
            il_molratio__isnull=False,
            hl_molratio__isnull=False,
            chl_molratio__isnull=False,
        )
        .select_related("ionizable_lipid")
        .values_list("il_molratio", "hl_molratio", "chl_molratio", "peg_molratio")
        [:2000]
    )
    # Get experiment values for color coding
    ternary_data = []
    for il, hl, ch, pg in formulations:
        total = (il or 0) + (hl or 0) + (ch or 0)
        if total > 0:
            ternary_data.append({
                "il": round((il or 0) / total, 4),
                "hl": round((hl or 0) / total, 4),
                "ch": round((ch or 0) / total, 4),
                "peg": round(pg or 0, 2),
            })

    optimizer_models = AIModel.objects.filter(model_type="formulation_optimizer")
    ctx = {
        "ternary_json": json.dumps(ternary_data),
        "optimizer_models": optimizer_models,
    }
    return render(request, "ai_models/optimize.html", ctx)
