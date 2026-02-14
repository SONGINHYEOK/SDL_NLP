"""
Workflow pipeline step executors.

Each step function receives (run, step) and returns an output dict.
The dispatcher `execute_step` chains inputs from the previous step
before calling the appropriate executor.
"""
import random
import uuid
from django.utils import timezone

from compounds.models import IonizableLipid, HelperLipid, Cholesterol, PEGLipid
from formulations.models import LNPFormulation
from experiments.models import Experiment, ExperimentResult
from equipment.models import Equipment, EquipmentStatus
from ai_models.models import AIModel, Prediction, GeneratedCandidate


# ─────────────────────── Utilities ───────────────────────


def _chain_input(run, step):
    """Copy previous step's output_data into this step's input_data."""
    prev = (
        run.steps.filter(step_order__lt=step.step_order, status="completed")
        .order_by("-step_order")
        .first()
    )
    if prev and prev.output_data:
        step.input_data = prev.output_data
        step.save(update_fields=["input_data"])


def _get_ai_model(run):
    """Return the run's ai_model or the first active AIModel."""
    if run.ai_model:
        return run.ai_model
    return AIModel.objects.filter(is_active=True).first()


def _log_equipment(equipment, status, message, metadata=None):
    """Create an EquipmentStatus log entry."""
    if equipment is None:
        return None
    return EquipmentStatus.objects.create(
        equipment=equipment,
        status=status,
        message=message,
        metadata=metadata or {},
    )


# ─────────────────────── Step 1: Design ───────────────────────


def execute_design(run, step):
    """
    Filter IonizableLipids by descriptor criteria, sample candidates,
    create GeneratedCandidate & Prediction records.
    """
    ai_model = _get_ai_model(run)

    # Filter lipids: MW 500-900, prefer biodegradable linkers (ester/disulfide)
    qs = IonizableLipid.objects.filter(
        molecular_weight__gte=500, molecular_weight__lte=900
    )
    total_search_space = qs.count()

    # Prefer biodegradable linkers
    bio_qs = qs.filter(has_ester=True) | qs.filter(has_disulfide=True)
    if bio_qs.exists() and bio_qs.count() >= 8:
        pool = bio_qs
    else:
        pool = qs

    pool_count = pool.count()
    if pool_count == 0:
        # Fallback: use any lipid
        pool = IonizableLipid.objects.all()
        pool_count = pool.count()
        total_search_space = pool_count

    # Sample 8-15 candidates
    n_candidates = min(random.randint(8, 15), pool_count)
    if pool_count <= n_candidates:
        sampled = list(pool[:n_candidates])
    else:
        ids = list(pool.values_list("id", flat=True))
        sampled_ids = random.sample(ids, n_candidates)
        sampled = list(IonizableLipid.objects.filter(id__in=sampled_ids))

    # Create GeneratedCandidate records
    candidates_out = []
    generated_objs = []
    for rank, lipid in enumerate(sampled, start=1):
        desc = lipid.descriptor_dict
        efficacy = round(random.uniform(0.55, 0.95), 3)
        stability = round(random.uniform(0.50, 0.90), 3)
        safety = round(random.uniform(0.60, 0.95), 3)

        gc = GeneratedCandidate(
            ai_model=ai_model,
            generation=run.iteration,
            smiles=lipid.smiles,
            predicted_properties=desc,
            efficacy_score=efficacy,
            stability_score=stability,
            safety_score=safety,
            pareto_rank=rank,
            status=GeneratedCandidate.Status.GENERATED,
        )
        generated_objs.append(gc)
        candidates_out.append({
            "lipid_id": lipid.pk,
            "name": lipid.name,
            "smiles": lipid.smiles,
            "mw": desc.get("molecular_weight"),
            "logp": desc.get("logp"),
            "efficacy_score": efficacy,
            "stability_score": stability,
            "safety_score": safety,
            "pareto_rank": rank,
        })

    if ai_model:
        GeneratedCandidate.objects.bulk_create(generated_objs)
        # Mark top candidate as selected
        top_gc = GeneratedCandidate.objects.filter(
            ai_model=ai_model, generation=run.iteration
        ).order_by("pareto_rank").first()
        if top_gc:
            top_gc.status = GeneratedCandidate.Status.SELECTED
            top_gc.save(update_fields=["status"])

    # Best candidate (rank 1)
    top = candidates_out[0] if candidates_out else {}

    # Create Prediction record
    if ai_model and top:
        Prediction.objects.create(
            ai_model=ai_model,
            input_data={"descriptors": top, "search_space": total_search_space},
            output_data={
                "efficacy": top.get("efficacy_score"),
                "stability": top.get("stability_score"),
                "safety": top.get("safety_score"),
            },
            confidence=round(random.uniform(0.70, 0.92), 3),
        )

    return {
        "top_candidate": top,
        "candidates": candidates_out,
        "search_space": {
            "total_lipids": total_search_space,
            "filtered_pool": pool_count,
            "sampled": n_candidates,
        },
    }


# ─────────────────────── Step 2: Synthesize ───────────────────────


def execute_synthesize(run, step):
    """
    Look up the top candidate lipid and simulate synthesis conditions
    based on its physicochemical properties.
    """
    inp = step.input_data or {}
    top = inp.get("top_candidate", {})
    lipid_id = top.get("lipid_id")

    lipid = None
    if lipid_id:
        lipid = IonizableLipid.objects.filter(pk=lipid_id).first()

    # Derive synthesis conditions from lipid properties
    mw = (lipid.molecular_weight or 700) if lipid else 700
    logp = (lipid.logp or 8.0) if lipid else 8.0

    # Higher MW → higher temp & longer time
    base_temp = 60 + (mw - 500) * 0.05
    temp = round(base_temp + random.uniform(-5, 5), 1)
    time_h = round(2.0 + (mw - 500) * 0.005 + random.uniform(-0.5, 0.5), 1)

    # Solvent based on logP
    if logp > 10:
        solvent = "DCM / MeOH (3:1)"
    elif logp > 6:
        solvent = "THF / EtOH (2:1)"
    else:
        solvent = "EtOH / Water (4:1)"

    catalyst = random.choice(["EDC/NHS", "DMAP", "DCC", "HATU"])

    # Yield & purity influenced by MW (lighter molecules → higher yield)
    yield_base = 90 - (mw - 500) * 0.04
    yield_pct = round(max(55, min(98, yield_base + random.uniform(-8, 8))), 1)
    purity_pct = round(max(88, min(99.9, 96 + random.uniform(-4, 3))), 1)

    batch_id = f"BATCH-{run.pk:03d}-{random.randint(1000, 9999)}"

    # Update GeneratedCandidate status
    ai_model = _get_ai_model(run)
    if ai_model and lipid:
        GeneratedCandidate.objects.filter(
            ai_model=ai_model,
            smiles=lipid.smiles,
            status=GeneratedCandidate.Status.SELECTED,
        ).update(status=GeneratedCandidate.Status.SYNTHESIZED)

    # Equipment logs
    eq = step.equipment or Equipment.objects.filter(equipment_type="liquid_handler").first()
    _log_equipment(eq, "running", f"Synthesis started: {batch_id}",
                   {"batch_id": batch_id, "workflow_run": run.pk})
    _log_equipment(eq, "idle", f"Synthesis complete: yield {yield_pct}%",
                   {"batch_id": batch_id, "yield_pct": yield_pct, "purity_pct": purity_pct})

    return {
        "lipid_id": lipid.pk if lipid else None,
        "lipid_name": lipid.name if lipid else "Unknown",
        "batch_id": batch_id,
        "synthesis_conditions": {
            "temperature_c": temp,
            "reaction_time_h": time_h,
            "solvent": solvent,
            "catalyst": catalyst,
        },
        "yield_pct": yield_pct,
        "purity_pct": purity_pct,
        "qc": {
            "ms_confirmed": purity_pct > 90,
            "nmr_purity": round(purity_pct - random.uniform(0, 2), 1),
            "hplc_purity": purity_pct,
        },
    }


# ─────────────────────── Step 3: Formulate ───────────────────────


def execute_formulate(run, step):
    """
    Formulate an LNP using the synthesized lipid and randomly chosen
    helper components, creating a real LNPFormulation record.
    """
    inp = step.input_data or {}
    lipid_id = inp.get("lipid_id")

    lipid = None
    if lipid_id:
        lipid = IonizableLipid.objects.filter(pk=lipid_id).first()
    if lipid is None:
        lipid = IonizableLipid.objects.order_by("?").first()

    # Pick helper components
    helper = HelperLipid.objects.order_by("?").first()
    chol = Cholesterol.objects.order_by("?").first()
    peg = PEGLipid.objects.order_by("?").first()

    # Molar ratios — based on DB averages with perturbation
    # Typical: IL 50, HL 10, Chol 38.5, PEG 1.5
    il_r = 50.0 + random.uniform(-5, 5)
    hl_r = 10.0 + random.uniform(-3, 3)
    chl_r = 38.5 + random.uniform(-4, 4)
    peg_r = 1.5 + random.uniform(-0.5, 0.5)

    # Normalize to 100
    total = il_r + hl_r + chl_r + peg_r
    il_r = round(il_r / total * 100, 1)
    hl_r = round(hl_r / total * 100, 1)
    chl_r = round(chl_r / total * 100, 1)
    peg_r = round(100 - il_r - hl_r - chl_r, 1)

    np_ratio = round(random.uniform(4.0, 10.0), 1)

    # Create LNPFormulation record
    fid = f"WF{run.pk:03d}-F{uuid.uuid4().hex[:6].upper()}"
    formulation = LNPFormulation.objects.create(
        formulation_id=fid,
        ionizable_lipid=lipid,
        il_molratio=il_r,
        helper_lipid=helper,
        hl_molratio=hl_r if helper else None,
        cholesterol=chol,
        chl_molratio=chl_r if chol else None,
        peg_lipid=peg,
        peg_molratio=peg_r if peg else None,
        il_to_na_chargeratio=np_ratio,
        mixing_method=LNPFormulation.MixingMethod.MICROFLUIDICS,
        source=LNPFormulation.Source.DESIGNED,
    )

    # Equipment logs
    eq = step.equipment or Equipment.objects.filter(equipment_type="microfluidic").first()
    _log_equipment(eq, "running", f"Microfluidic mixing started: {fid}",
                   {"formulation_id": fid, "workflow_run": run.pk})
    _log_equipment(eq, "idle", f"Formulation complete: {fid}",
                   {"formulation_id": fid, "np_ratio": np_ratio})

    components = {
        "ionizable_lipid": {"id": lipid.pk, "name": lipid.name, "ratio": il_r},
    }
    if helper:
        components["helper_lipid"] = {"id": helper.pk, "name": helper.name, "ratio": hl_r}
    if chol:
        components["cholesterol"] = {"id": chol.pk, "name": chol.name, "ratio": chl_r}
    if peg:
        components["peg_lipid"] = {"id": peg.pk, "name": peg.name, "ratio": peg_r}

    return {
        "formulation_pk": formulation.pk,
        "formulation_id": fid,
        "components": components,
        "composition_str": formulation.composition_str,
        "mixing_parameters": {
            "method": "microfluidics",
            "flow_rate_ml_min": round(random.uniform(6, 18), 1),
            "tfr": round(random.uniform(8, 20), 1),
            "frr": round(random.uniform(2, 5), 1),
        },
        "np_ratio": np_ratio,
    }


# ─────────────────────── Step 4: Analyze ───────────────────────


def execute_analyze(run, step):
    """
    Create Experiment + ExperimentResult records for the formulation.
    Compare against DB benchmarks.
    """
    inp = step.input_data or {}
    formulation_pk = inp.get("formulation_pk")

    formulation = None
    if formulation_pk:
        formulation = LNPFormulation.objects.filter(pk=formulation_pk).first()
    if formulation is None:
        formulation = LNPFormulation.objects.order_by("-created_at").first()

    # Create Experiment
    exp_id = f"EXP-WF{run.pk:03d}-{uuid.uuid4().hex[:6].upper()}"
    experiment = Experiment.objects.create(
        experiment_id=exp_id,
        model_name="HEK293T",
        model_type=Experiment.ModelType.IN_VITRO,
        model_target="Luciferase mRNA",
        route=Experiment.Route.IN_VITRO,
        cargo=Experiment.CargoType.MRNA,
        cargo_type="FLuc mRNA",
        dose_ug=0.5,
    )

    # Simulate measurements
    diameter = round(random.uniform(60, 150), 1)
    pdi = round(random.uniform(0.04, 0.30), 3)
    zeta = round(random.uniform(-40, -5), 1)
    ee_pct = round(random.uniform(75, 99), 1)
    luminescence = round(random.uniform(0.3, 1.0), 4)

    # Create ExperimentResult records
    results_data = [
        ("diameter", diameter, f"LNP-{exp_id}-DLS"),
        ("zeta_potential", zeta, f"LNP-{exp_id}-ZETA"),
        ("luminescence_normalized", luminescence, f"LNP-{exp_id}-LUM"),
    ]
    for method, value, lnp_id in results_data:
        if formulation:
            ExperimentResult.objects.create(
                lnp_id=lnp_id,
                experiment=experiment,
                formulation=formulation,
                method=method,
                value=value,
            )

    # DB benchmarks
    benchmarks = {}
    for m in ["diameter", "zeta_potential", "luminescence_normalized"]:
        from django.db.models import Avg
        avg_val = ExperimentResult.objects.filter(method=m).aggregate(avg=Avg("value"))["avg"]
        if avg_val is not None:
            benchmarks[m] = round(avg_val, 3)

    # Equipment logs
    eq = step.equipment or Equipment.objects.filter(equipment_type="dls").first()
    _log_equipment(eq, "running", f"DLS measurement started: {exp_id}",
                   {"experiment_id": exp_id, "workflow_run": run.pk})
    _log_equipment(eq, "idle", f"Analysis complete: diameter={diameter}nm",
                   {"experiment_id": exp_id, "diameter": diameter, "pdi": pdi})

    # Update GeneratedCandidate status → tested
    ai_model = _get_ai_model(run)
    if ai_model and formulation:
        GeneratedCandidate.objects.filter(
            ai_model=ai_model,
            smiles=formulation.ionizable_lipid.smiles,
            status=GeneratedCandidate.Status.SYNTHESIZED,
        ).update(status=GeneratedCandidate.Status.TESTED)

    qc_pass = diameter < 200 and pdi < 0.3 and ee_pct > 80

    return {
        "experiment_id": exp_id,
        "formulation_pk": formulation.pk if formulation else None,
        "measurements": {
            "diameter_nm": diameter,
            "pdi": pdi,
            "zeta_potential_mV": zeta,
            "encapsulation_efficiency_pct": ee_pct,
        },
        "functional_assay": {
            "luminescence_normalized": luminescence,
            "cell_line": "HEK293T",
            "cargo": "FLuc mRNA",
            "dose_ug": 0.5,
        },
        "db_benchmarks": benchmarks,
        "qc_pass": qc_pass,
    }


# ─────────────────────── Step 5: Learn ───────────────────────


def execute_learn(run, step):
    """
    Update AIModel metrics (slight improvement), generate feature
    importance and next-iteration suggestions.
    """
    ai_model = _get_ai_model(run)
    inp = step.input_data or {}
    measurements = inp.get("measurements", {})

    before_metrics = {}
    after_metrics = {}

    if ai_model:
        before_metrics = dict(ai_model.metrics) if ai_model.metrics else {}

        # Slight improvement in metrics
        old_r2 = before_metrics.get("r2", 0.80)
        old_rmse = before_metrics.get("rmse", 0.12)

        new_r2 = round(min(0.99, old_r2 + random.uniform(0.005, 0.02)), 4)
        new_rmse = round(max(0.01, old_rmse - random.uniform(0.002, 0.01)), 4)

        ai_model.metrics = {"r2": new_r2, "rmse": new_rmse}
        ai_model.training_data_count = (ai_model.training_data_count or 0) + random.randint(5, 20)
        ai_model.save(update_fields=["metrics", "training_data_count", "updated_at"])

        after_metrics = {"r2": new_r2, "rmse": new_rmse}

    # Feature importance (descriptor-based)
    descriptors = [
        "molecular_weight", "logp", "tpsa", "hbd", "hba",
        "rotatable_bonds", "vdw_volume", "fsp3", "nitrogen_count",
    ]
    importances = {}
    raw = {d: random.uniform(0.02, 0.25) for d in descriptors}
    total = sum(raw.values())
    for d in descriptors:
        importances[d] = round(raw[d] / total, 4)

    # Next iteration suggestions based on analyze results
    suggestions = []
    pdi = measurements.get("pdi", 0.15)
    diameter = measurements.get("diameter_nm", 80)
    zeta = measurements.get("zeta_potential_mV", -20)
    ee = measurements.get("encapsulation_efficiency_pct", 90)

    if pdi > 0.2:
        suggestions.append("Increase PEG-lipid molar ratio by 0.3-0.5 to reduce PDI")
    if diameter > 120:
        suggestions.append("Increase microfluidic flow rate or reduce IL ratio to decrease particle size")
    if zeta > -10:
        suggestions.append("Adjust N/P ratio to improve surface charge for colloidal stability")
    if ee < 85:
        suggestions.append("Optimize N/P ratio (increase to 6-8) to improve encapsulation efficiency")
    if not suggestions:
        suggestions.append("Results within optimal range. Consider exploring novel head-group chemistries for next iteration.")

    return {
        "ai_model": ai_model.name if ai_model else "N/A",
        "performance": {
            "before": before_metrics,
            "after": after_metrics,
            "training_data_count": ai_model.training_data_count if ai_model else 0,
        },
        "feature_importance": importances,
        "iteration_summary": {
            "iteration": run.iteration,
            "candidates_evaluated": GeneratedCandidate.objects.filter(
                ai_model=ai_model, generation=run.iteration
            ).count() if ai_model else 0,
            "qc_pass": inp.get("qc_pass", None),
        },
        "suggestions": suggestions,
    }


# ─────────────────────── Dispatcher ───────────────────────

_EXECUTORS = {
    "design": execute_design,
    "synthesize": execute_synthesize,
    "formulate": execute_formulate,
    "analyze": execute_analyze,
    "learn": execute_learn,
}


def execute_step(run, step):
    """
    Main dispatcher: chain input from previous step, then call the
    appropriate executor.
    """
    _chain_input(run, step)
    executor = _EXECUTORS.get(step.step_type)
    if executor is None:
        return {"result": "ok", "message": f"No executor for {step.step_type}"}
    return executor(run, step)
