from django.db import models
from django.utils import timezone


class Reagent(models.Model):
    """Reagent / consumable master record."""

    class Category(models.TextChoices):
        SOLVENT = "solvent", "Solvent"
        BUFFER = "buffer", "Buffer"
        LIPID_STOCK = "lipid_stock", "Lipid Stock"
        MRNA_CARGO = "mrna_cargo", "mRNA Cargo"
        CONSUMABLE = "consumable", "Consumable"
        REAGENT = "reagent", "Reagent"

    class Unit(models.TextChoices):
        ML = "mL", "mL"
        L = "L", "L"
        MG = "mg", "mg"
        G = "g", "g"
        UG = "ug", "\u00b5g"
        UNITS = "units", "units"

    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    cas_number = models.CharField(max_length=50, blank=True, default="")
    unit = models.CharField(max_length=10, choices=Unit.choices)
    storage_conditions = models.CharField(max_length=100, blank=True, default="")
    minimum_stock = models.FloatField(default=0, help_text="Low-stock alert threshold")
    reorder_point = models.FloatField(default=0, help_text="Reorder trigger quantity")
    pipeline_steps = models.JSONField(default=list, blank=True, help_text='e.g. ["synthesize","formulate"]')
    metadata = models.JSONField(default=dict, blank=True, help_text="Supplier, purity, catalog no., etc.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"

    @property
    def current_stock(self):
        return sum(
            s.quantity
            for s in self.stocks.filter(is_active=True)
            if not s.is_expired
        )

    @property
    def stock_status(self):
        stock = self.current_stock
        if stock <= 0 or stock < self.minimum_stock * 0.5:
            return "critical"
        if stock < self.minimum_stock:
            return "warning"
        return "good"


class ReagentStock(models.Model):
    """Individual lot / bottle of a reagent."""

    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE, related_name="stocks")
    lot_number = models.CharField(max_length=100)
    quantity = models.FloatField(help_text="Current remaining quantity")
    initial_quantity = models.FloatField(help_text="Quantity when received")
    location = models.CharField(max_length=200, blank=True, default="")
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["expiry_date", "received_at"]

    def __str__(self):
        return f"{self.reagent.name} - Lot {self.lot_number} ({self.quantity} {self.reagent.get_unit_display()})"

    @property
    def is_expired(self):
        if self.expiry_date is None:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def usage_pct(self):
        if self.initial_quantity <= 0:
            return 0
        return round((1 - self.quantity / self.initial_quantity) * 100, 1)


class ReagentConsumption(models.Model):
    """Record of reagent consumed during a workflow step."""

    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE, related_name="consumptions")
    stock_lot = models.ForeignKey(ReagentStock, on_delete=models.SET_NULL, null=True, blank=True, related_name="consumptions")
    workflow_step = models.ForeignKey(
        "workflow.WorkflowStep", on_delete=models.SET_NULL, null=True, blank=True, related_name="reagent_consumptions"
    )
    quantity_used = models.FloatField()
    batch_id = models.CharField(max_length=100, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.reagent.name}: -{self.quantity_used} {self.reagent.get_unit_display()} @ {self.timestamp}"
