"""
Seed script for reagent inventory and equipment maintenance records.

Usage:
    python manage.py shell < scripts/seed_inventory.py
    OR
    python manage.py runscript seed_inventory  (with django-extensions)
"""
import sys
import os
from datetime import date, timedelta

import django

# Ensure Django is configured
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
if not django.conf.settings.configured:
    django.setup()

from inventory.models import Reagent, ReagentStock
from equipment.models import Equipment, MaintenanceRecord

# ───────────────────── Reagent Definitions ─────────────────────

REAGENTS = [
    # Solvents
    {
        "name": "Ethanol (200 proof)",
        "category": "solvent",
        "cas_number": "64-17-5",
        "unit": "mL",
        "storage_conditions": "RT, flammable cabinet",
        "minimum_stock": 500.0,
        "reorder_point": 1000.0,
        "pipeline_steps": ["synthesize"],
        "metadata": {"supplier": "Sigma-Aldrich", "purity": "99.5%", "catalog": "E7023"},
    },
    {
        "name": "Chloroform / DCM",
        "category": "solvent",
        "cas_number": "67-66-3",
        "unit": "mL",
        "storage_conditions": "RT, fume hood",
        "minimum_stock": 200.0,
        "reorder_point": 500.0,
        "pipeline_steps": ["synthesize"],
        "metadata": {"supplier": "Fisher Scientific", "purity": "99.8%", "catalog": "C298-4"},
    },
    # Buffers
    {
        "name": "Citrate Buffer pH 4.0",
        "category": "buffer",
        "cas_number": "77-92-9",
        "unit": "mL",
        "storage_conditions": "4C",
        "minimum_stock": 300.0,
        "reorder_point": 600.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "Teknova", "concentration": "25 mM", "catalog": "Q2446"},
    },
    {
        "name": "PBS Buffer pH 7.4",
        "category": "buffer",
        "cas_number": "7647-14-5",
        "unit": "mL",
        "storage_conditions": "RT",
        "minimum_stock": 500.0,
        "reorder_point": 1000.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "Gibco", "concentration": "1X", "catalog": "10010-023"},
    },
    # mRNA Cargo
    {
        "name": "FLuc mRNA (1 mg/mL)",
        "category": "mrna_cargo",
        "cas_number": "",
        "unit": "ug",
        "storage_conditions": "-80C",
        "minimum_stock": 500.0,
        "reorder_point": 1000.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "TriLink", "modification": "N1-methylpseudouridine", "catalog": "L-7202"},
    },
    # Lipid stocks
    {
        "name": "MC3 (DLin-MC3-DMA) Stock",
        "category": "lipid_stock",
        "cas_number": "1224606-06-7",
        "unit": "mg",
        "storage_conditions": "-20C, N2 atmosphere",
        "minimum_stock": 100.0,
        "reorder_point": 250.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "BroadPharm", "purity": ">98%", "catalog": "BP-25404"},
    },
    {
        "name": "DSPC Stock",
        "category": "lipid_stock",
        "cas_number": "816-94-4",
        "unit": "mg",
        "storage_conditions": "-20C",
        "minimum_stock": 100.0,
        "reorder_point": 250.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "Avanti Polar Lipids", "purity": ">99%", "catalog": "850365"},
    },
    {
        "name": "Cholesterol (Plant-derived)",
        "category": "lipid_stock",
        "cas_number": "57-88-5",
        "unit": "mg",
        "storage_conditions": "-20C",
        "minimum_stock": 200.0,
        "reorder_point": 500.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "Sigma-Aldrich", "purity": ">99%", "catalog": "C8667"},
    },
    {
        "name": "DMG-PEG2000 Stock",
        "category": "lipid_stock",
        "cas_number": "",
        "unit": "mg",
        "storage_conditions": "-20C",
        "minimum_stock": 50.0,
        "reorder_point": 100.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "Avanti Polar Lipids", "purity": ">99%", "catalog": "880150"},
    },
    # Consumables
    {
        "name": "Microfluidic Cartridge",
        "category": "consumable",
        "cas_number": "",
        "unit": "units",
        "storage_conditions": "RT, clean room",
        "minimum_stock": 10.0,
        "reorder_point": 20.0,
        "pipeline_steps": ["formulate"],
        "metadata": {"supplier": "Precision NanoSystems", "type": "NanoAssemblr", "catalog": "NIT0001"},
    },
    {
        "name": "DLS Cuvette",
        "category": "consumable",
        "cas_number": "",
        "unit": "units",
        "storage_conditions": "RT",
        "minimum_stock": 20.0,
        "reorder_point": 50.0,
        "pipeline_steps": ["analyze"],
        "metadata": {"supplier": "Malvern Panalytical", "type": "DTS0012", "catalog": "DTS0012"},
    },
    {
        "name": "96-Well Plate (Black)",
        "category": "consumable",
        "cas_number": "",
        "unit": "units",
        "storage_conditions": "RT",
        "minimum_stock": 10.0,
        "reorder_point": 25.0,
        "pipeline_steps": ["analyze"],
        "metadata": {"supplier": "Corning", "type": "Flat-bottom, black", "catalog": "3925"},
    },
]

# ───────────────────── Create Reagents & Stock ─────────────────────

today = date.today()
created_reagents = 0
created_stocks = 0

for rdef in REAGENTS:
    reagent, created = Reagent.objects.get_or_create(
        name=rdef["name"],
        defaults={
            "category": rdef["category"],
            "cas_number": rdef["cas_number"],
            "unit": rdef["unit"],
            "storage_conditions": rdef["storage_conditions"],
            "minimum_stock": rdef["minimum_stock"],
            "reorder_point": rdef["reorder_point"],
            "pipeline_steps": rdef["pipeline_steps"],
            "metadata": rdef["metadata"],
        },
    )
    if created:
        created_reagents += 1

    # Create 2 lots per reagent if none exist
    if reagent.stocks.count() == 0:
        min_stock = rdef["minimum_stock"]

        # Certain items get low stock for demo alerts
        low_stock_items = {"Microfluidic Cartridge", "DLS Cuvette", "FLuc mRNA (1 mg/mL)"}
        is_low = rdef["name"] in low_stock_items

        # Lot 1: partially consumed
        initial_1 = min_stock * 2.0
        current_1 = min_stock * 0.3 if is_low else min_stock * 0.6
        ReagentStock.objects.create(
            reagent=reagent,
            lot_number=f"LOT-{reagent.pk:03d}-A",
            quantity=current_1,
            initial_quantity=initial_1,
            location=f"Shelf-{reagent.get_category_display()[:3].upper()}-{reagent.pk}",
            expiry_date=today + timedelta(days=60),
        )
        created_stocks += 1

        # Lot 2: for low-stock items, this lot is nearly depleted
        initial_2 = min_stock * 3.0
        current_2 = min_stock * 0.1 if is_low else initial_2
        ReagentStock.objects.create(
            reagent=reagent,
            lot_number=f"LOT-{reagent.pk:03d}-B",
            quantity=current_2,
            initial_quantity=initial_2,
            location=f"Shelf-{reagent.get_category_display()[:3].upper()}-{reagent.pk}",
            expiry_date=today + timedelta(days=365),
        )
        created_stocks += 1

print(f"Reagents: {created_reagents} created ({Reagent.objects.count()} total)")
print(f"Stock lots: {created_stocks} created ({ReagentStock.objects.count()} total)")


# ───────────────────── Equipment Maintenance Records ─────────────────────

MAINTENANCE_RECORDS = [
    # DLS: calibration completed + next scheduled
    {
        "equipment_type": "dls",
        "type": "calibration",
        "status": "completed",
        "description": "Annual DLS size calibration with NIST-traceable standards (60nm, 100nm, 200nm polystyrene)",
        "scheduled_date": today - timedelta(days=15),
        "completed_date": today - timedelta(days=14),
        "next_due_date": today + timedelta(days=166),
        "calibration_data": {"std_60nm": 61.2, "std_100nm": 99.8, "std_200nm": 201.5, "result": "PASS"},
        "cost": 350.00,
    },
    {
        "equipment_type": "dls",
        "type": "calibration",
        "status": "scheduled",
        "description": "Semi-annual DLS calibration check",
        "scheduled_date": today + timedelta(days=166),
        "calibration_data": {},
    },
    # Microfluidic: preventive completed + cleaning scheduled
    {
        "equipment_type": "microfluidic",
        "type": "preventive",
        "status": "completed",
        "description": "Microfluidic mixer channel inspection and O-ring replacement",
        "scheduled_date": today - timedelta(days=30),
        "completed_date": today - timedelta(days=29),
        "next_due_date": today + timedelta(days=60),
        "cost": 180.00,
    },
    {
        "equipment_type": "microfluidic",
        "type": "cleaning",
        "status": "scheduled",
        "description": "Flush channels with ethanol/water and validate with blank run",
        "scheduled_date": today + timedelta(days=7),
    },
    # Liquid Handler: calibration OVERDUE (demo alert)
    {
        "equipment_type": "liquid_handler",
        "type": "calibration",
        "status": "overdue",
        "description": "Liquid handler pipette tip volume calibration (1-200 uL range)",
        "scheduled_date": today - timedelta(days=5),
        "calibration_data": {"last_cal_date": str(today - timedelta(days=185)), "drift_detected": True},
    },
    # Plate Reader: software update completed
    {
        "equipment_type": "plate_reader",
        "type": "software_update",
        "status": "completed",
        "description": "Firmware v3.2.1 update with improved luminescence sensitivity algorithm",
        "scheduled_date": today - timedelta(days=7),
        "completed_date": today - timedelta(days=7),
        "next_due_date": today + timedelta(days=180),
        "calibration_data": {"firmware_version": "3.2.1", "previous_version": "3.1.4"},
    },
    # HPLC: column replacement scheduled
    {
        "equipment_type": "hplc",
        "type": "corrective",
        "status": "scheduled",
        "description": "Replace C18 analytical column (>5000 injections) and validate with system suitability test",
        "scheduled_date": today + timedelta(days=14),
        "cost": 620.00,
    },
]

created_maint = 0
for mdef in MAINTENANCE_RECORDS:
    eq = Equipment.objects.filter(equipment_type=mdef["equipment_type"]).first()
    if eq is None:
        print(f"  [SKIP] No equipment of type '{mdef['equipment_type']}' found")
        continue

    # Check if similar record already exists
    exists = MaintenanceRecord.objects.filter(
        equipment=eq,
        maintenance_type=mdef["type"],
        scheduled_date=mdef["scheduled_date"],
    ).exists()
    if exists:
        continue

    MaintenanceRecord.objects.create(
        equipment=eq,
        maintenance_type=mdef["type"],
        status=mdef["status"],
        description=mdef["description"],
        scheduled_date=mdef["scheduled_date"],
        completed_date=mdef.get("completed_date"),
        next_due_date=mdef.get("next_due_date"),
        calibration_data=mdef.get("calibration_data", {}),
        cost=mdef.get("cost"),
    )
    created_maint += 1

print(f"Maintenance records: {created_maint} created ({MaintenanceRecord.objects.count()} total)")
print("Done!")
