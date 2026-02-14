"""Create demo equipment and workflow data for SDL demonstration."""
import os, sys, django
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from equipment.models import Equipment, EquipmentStatus
from workflow.models import WorkflowRun, WorkflowStep
from ai_models.models import AIModel

# Equipment (SDL)
equips = [
    ("Hamilton STAR", "liquid_handler", "Hamilton", "STAR", "rest_api", True),
    ("NanoAssemblr Ignite", "microfluidic", "Precision NanoSystems", "Ignite", "rest_api", True),
    ("Zetasizer Ultra", "dls", "Malvern Panalytical", "Ultra", "serial", True),
    ("Infinite M200 Pro", "plate_reader", "Tecan", "M200 Pro", "rest_api", False),
    ("Agilent 1260 Infinity", "hplc", "Agilent", "1260", "opcua", False),
]
for name, etype, mfr, model, proto, connected in equips:
    eq, _ = Equipment.objects.get_or_create(
        name=name, defaults=dict(
            equipment_type=etype, manufacturer=mfr, model_number=model,
            protocol=proto, is_connected=connected
        )
    )
    EquipmentStatus.objects.get_or_create(
        equipment=eq, status="idle" if connected else "offline"
    )

print(f"Equipment: {Equipment.objects.count()}")

# AI Models
models_data = [
    ("LNP-Efficacy-RF", "1.0", "property_predictor", {"r2": 0.82, "rmse": 0.15}, 19797, True),
    ("LNP-StructGen-VAE", "0.3", "structure_generator", {"validity": 0.94, "novelty": 0.87}, 13339, False),
    ("LNP-FormOpt-BO", "0.2", "formulation_optimizer", {"improvement": "23%"}, 5000, False),
]
for name, ver, mtype, metrics, count, active in models_data:
    AIModel.objects.get_or_create(
        name=name, version=ver, defaults=dict(
            model_type=mtype, metrics=metrics,
            training_data_count=count, is_active=active
        )
    )
print(f"AI Models: {AIModel.objects.count()}")

# Demo Workflow
wf, _ = WorkflowRun.objects.get_or_create(
    name="LNP-Opt-Cycle-1",
    defaults=dict(description="First optimization cycle for mRNA delivery", status="completed", iteration=1)
)
steps = [
    (1, "design", "completed"),
    (2, "synthesize", "completed"),
    (3, "formulate", "completed"),
    (4, "analyze", "completed"),
    (5, "learn", "completed"),
]
for order, stype, status in steps:
    WorkflowStep.objects.get_or_create(
        workflow=wf, step_order=order, defaults=dict(step_type=stype, status=status)
    )

wf2, _ = WorkflowRun.objects.get_or_create(
    name="LNP-Opt-Cycle-2",
    defaults=dict(description="Second optimization with updated model", status="running", iteration=2)
)
for order, stype, status in [(1,"design","completed"),(2,"synthesize","running"),(3,"formulate","pending"),(4,"analyze","pending"),(5,"learn","pending")]:
    WorkflowStep.objects.get_or_create(
        workflow=wf2, step_order=order, defaults=dict(step_type=stype, status=status)
    )

print(f"Workflows: {WorkflowRun.objects.count()}")
print("Demo data created!")
