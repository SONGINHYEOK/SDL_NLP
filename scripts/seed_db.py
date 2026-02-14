"""
LNPDB Seed Script
Loads 19,797 records from LNPDB.csv into Django ORM.
Run: python manage.py runscript seed_db (via django-extensions)
Or:  python manage.py shell < scripts/seed_db.py
"""
import csv
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from compounds.models import IonizableLipid, HeadGroup, Linker, Tail, HelperLipid, Cholesterol, PEGLipid
from formulations.models import LNPFormulation
from experiments.models import Experiment, ExperimentResult

CSV_PATH = BASE / "data" / "seed" / "LNPDB.csv"


def safe_float(val):
    try:
        v = float(val)
        return v if v == v else None  # NaN check
    except (ValueError, TypeError):
        return None


def safe_int(val):
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def safe_str(val):
    if val is None or val == "None" or val == "NA" or val == "":
        return ""
    return str(val).strip()


def run():
    print(f"Loading LNPDB from {CSV_PATH}")

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Total rows: {len(rows)}")

    # ── Phase 1: Collect unique component values ──
    heads, linkers, tails = {}, {}, {}
    helpers, chols, pegs = {}, {}, {}

    for r in rows:
        h = safe_str(r.get("IL_head_name"))
        if h:
            heads[h] = safe_str(r.get("IL_head_SMILES"))

        lk = safe_str(r.get("IL_linker_name"))
        if lk:
            linkers[lk] = safe_str(r.get("IL_linker_SMILES"))

        for t_col, s_col in [("IL_tail1_name", "IL_tail1_SMILES"), ("IL_tail2_name", "IL_tail2_SMILES")]:
            t = safe_str(r.get(t_col))
            if t:
                tails[t] = safe_str(r.get(s_col))

        hl = safe_str(r.get("HL_name"))
        if hl:
            helpers[hl] = safe_str(r.get("HL_SMILES"))

        ch = safe_str(r.get("CHL_name"))
        if ch:
            chols[ch] = safe_str(r.get("CHL_SMILES"))

        pg = safe_str(r.get("PEG_name"))
        if pg:
            pegs[pg] = safe_str(r.get("PEG_SMILES"))

    print(f"Unique: heads={len(heads)}, linkers={len(linkers)}, tails={len(tails)}")
    print(f"Unique: helpers={len(helpers)}, cholesterols={len(chols)}, PEGs={len(pegs)}")

    # ── Phase 2: Bulk create components ──
    with transaction.atomic():
        HeadGroup.objects.all().delete()
        Linker.objects.all().delete()
        Tail.objects.all().delete()
        HelperLipid.objects.all().delete()
        Cholesterol.objects.all().delete()
        PEGLipid.objects.all().delete()
        IonizableLipid.objects.all().delete()
        LNPFormulation.objects.all().delete()
        Experiment.objects.all().delete()
        ExperimentResult.objects.all().delete()

        head_objs = {n: HeadGroup.objects.create(name=n, smiles=s) for n, s in heads.items()}
        linker_objs = {n: Linker.objects.create(name=n, smiles=s) for n, s in linkers.items()}
        tail_objs = {n: Tail.objects.create(name=n, smiles=s) for n, s in tails.items()}
        helper_objs = {n: HelperLipid.objects.create(name=n, smiles=s) for n, s in helpers.items()}
        chol_objs = {n: Cholesterol.objects.create(name=n, smiles=s) for n, s in chols.items()}
        peg_objs = {n: PEGLipid.objects.create(name=n, smiles=s) for n, s in pegs.items()}

        print("Components created.")

    # ── Phase 3: Create IonizableLipids (deduplicated by name+smiles) ──
    print("Creating ionizable lipids...")
    il_cache = {}
    il_bulk = []
    seen_il = set()

    for r in rows:
        il_name = safe_str(r.get("IL_name"))
        il_smiles = safe_str(r.get("IL_SMILES"))
        key = (il_name, il_smiles)
        if key in seen_il or not il_smiles:
            continue
        seen_il.add(key)

        il = IonizableLipid(
            name=il_name,
            smiles=il_smiles,
            protonated_smiles=safe_str(r.get("IL_protonated_SMILES")),
            head_group=head_objs.get(safe_str(r.get("IL_head_name"))),
            linker=linker_objs.get(safe_str(r.get("IL_linker_name"))),
            tail1=tail_objs.get(safe_str(r.get("IL_tail1_name"))),
            tail2=tail_objs.get(safe_str(r.get("IL_tail2_name"))),
            molecular_weight=safe_float(r.get("Molecular.Weight")),
            logp=safe_float(r.get("LogP")),
            tpsa=safe_float(r.get("Topological.Polar.Surface.Area")),
            heavy_atoms=safe_int(r.get("Heavy.Atoms")),
            rings=safe_int(r.get("Rings")),
            aromatic_rings=safe_int(r.get("Aromatic.Rings")),
            rotatable_bonds=safe_int(r.get("Rotatable.Bonds")),
            vdw_volume=safe_float(r.get("van.der.Waals.Molecular.Volume")),
            hbd=safe_int(r.get("Hydrogen.Bond.Donors")),
            hba=safe_int(r.get("Hydrogen.Bond.Acceptors")),
            molar_refractivity=safe_float(r.get("Molar.Refractivity")),
            fsp3=safe_float(r.get("Fraction.sp3.Carbons")),
            sp3_carbons=safe_int(r.get("sp3.Carbons")),
            nitrogen_count=safe_int(r.get("Nitrogen.Count")),
            has_ester=(r.get("has_ester") == "TRUE"),
            has_carbonate=(r.get("has_carbonate") == "TRUE"),
            has_disulfide=(r.get("has_disulfide") == "TRUE"),
            source="lnpdb",
            publication_link=safe_str(r.get("Publication_link")),
            publication_pmid=safe_str(r.get("Publication_PMID")),
        )
        il_bulk.append(il)

    with transaction.atomic():
        created_ils = IonizableLipid.objects.bulk_create(il_bulk, batch_size=2000)

    # Build lookup
    for il in created_ils:
        il_cache[(il.name, il.smiles)] = il

    print(f"Ionizable lipids: {len(created_ils)}")

    # ── Phase 4: Formulations + Experiments + Results ──
    print("Creating formulations, experiments, results...")
    form_cache = {}
    exp_cache = {}
    result_bulk = []

    for i, r in enumerate(rows):
        lnp_id = safe_str(r.get("LNP_ID"))
        if not lnp_id:
            continue

        # Get or create formulation
        form_id = safe_str(r.get("Formulation_ID")) or f"F_{lnp_id}"
        il_key = (safe_str(r.get("IL_name")), safe_str(r.get("IL_SMILES")))
        il_obj = il_cache.get(il_key)
        if not il_obj:
            continue

        if form_id not in form_cache:
            mixing = safe_str(r.get("Mixing_method"))
            form_cache[form_id] = LNPFormulation(
                formulation_id=form_id,
                ionizable_lipid=il_obj,
                il_molratio=safe_float(r.get("IL_molratio")) or 0,
                helper_lipid=helper_objs.get(safe_str(r.get("HL_name"))),
                hl_molratio=safe_float(r.get("HL_molratio")),
                cholesterol=chol_objs.get(safe_str(r.get("CHL_name"))),
                chl_molratio=safe_float(r.get("CHL_molratio")),
                peg_lipid=peg_objs.get(safe_str(r.get("PEG_name"))),
                peg_molratio=safe_float(r.get("PEG_molratio")),
                fifth_component_name=safe_str(r.get("fifthcomponent_name")),
                fifth_component_smiles=safe_str(r.get("fifthcomponent_SMILES")),
                fifth_component_molratio=safe_float(r.get("fifthcomponent_molratio")),
                il_to_na_massratio=safe_float(r.get("IL_to_nucleicacid_massratio")),
                il_to_na_chargeratio=safe_float(r.get("IL_to_nucleicacid_chargeratio")),
                mixing_method=mixing if mixing in ("microfluidics", "handmixed") else "microfluidics",
                aqueous_buffer=safe_str(r.get("Aqueous_buffer")),
                dialysis_buffer=safe_str(r.get("Dialysis_buffer")),
                source="lnpdb",
            )

        # Get or create experiment
        exp_id = safe_str(r.get("Experiment_ID")) or f"E_{lnp_id}"
        if exp_id not in exp_cache:
            model_type_raw = safe_str(r.get("Model_type"))
            route_raw = safe_str(r.get("Route_of_administration"))
            cargo_raw = safe_str(r.get("Cargo"))
            exp_cache[exp_id] = Experiment(
                experiment_id=exp_id,
                model_name=safe_str(r.get("Model")),
                model_type=model_type_raw if model_type_raw in ("in_vitro", "in_vivo") else "in_vitro",
                model_target=safe_str(r.get("Model_target")),
                route=route_raw if route_raw in ("in_vitro","intravenous","intramuscular","intradermal","intratracheal") else "in_vitro",
                cargo=cargo_raw if cargo_raw in ("mRNA","siRNA","pDNA") else "mRNA",
                cargo_type=safe_str(r.get("Cargo_type")),
                dose_ug=safe_float(r.get("Dose_ug_nucleicacid")),
                publication_link=safe_str(r.get("Publication_link")),
                publication_pmid=safe_str(r.get("Publication_PMID")),
            )

        # Result
        method_raw = safe_str(r.get("Experiment_method"))
        valid_methods = [c[0] for c in ExperimentResult.Method.choices]
        result_bulk.append({
            "lnp_id": lnp_id,
            "exp_id": exp_id,
            "form_id": form_id,
            "method": method_raw if method_raw in valid_methods else "luminescence_normalized",
            "batching": safe_str(r.get("Experiment_batching")),
            "value": safe_float(r.get("Experiment_value")) or 0,
        })

        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1}/{len(rows)} rows...")

    # Bulk save
    with transaction.atomic():
        form_list = list(form_cache.values())
        LNPFormulation.objects.bulk_create(form_list, batch_size=2000)
        form_db = {f.formulation_id: f for f in LNPFormulation.objects.all()}

        exp_list = list(exp_cache.values())
        Experiment.objects.bulk_create(exp_list, batch_size=2000)
        exp_db = {e.experiment_id: e for e in Experiment.objects.all()}

        er_objs = []
        for rb in result_bulk:
            form_obj = form_db.get(rb["form_id"])
            exp_obj = exp_db.get(rb["exp_id"])
            if form_obj and exp_obj:
                er_objs.append(ExperimentResult(
                    lnp_id=rb["lnp_id"],
                    experiment=exp_obj,
                    formulation=form_obj,
                    method=rb["method"],
                    batching=rb["batching"],
                    value=rb["value"],
                ))
        ExperimentResult.objects.bulk_create(er_objs, batch_size=3000)

    print(f"\nDone!")
    print(f"  HeadGroups: {HeadGroup.objects.count()}")
    print(f"  Linkers: {Linker.objects.count()}")
    print(f"  Tails: {Tail.objects.count()}")
    print(f"  IonizableLipids: {IonizableLipid.objects.count()}")
    print(f"  HelperLipids: {HelperLipid.objects.count()}")
    print(f"  Cholesterols: {Cholesterol.objects.count()}")
    print(f"  PEGLipids: {PEGLipid.objects.count()}")
    print(f"  Formulations: {LNPFormulation.objects.count()}")
    print(f"  Experiments: {Experiment.objects.count()}")
    print(f"  Results: {ExperimentResult.objects.count()}")


if __name__ == "__main__":
    run()
