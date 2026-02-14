from django.db import models


class Experiment(models.Model):
    """Experimental context: model system, cargo, route, publication."""

    class ModelType(models.TextChoices):
        IN_VITRO = "in_vitro", "In Vitro"
        IN_VIVO = "in_vivo", "In Vivo"

    class Route(models.TextChoices):
        IN_VITRO = "in_vitro", "In Vitro"
        IV = "intravenous", "Intravenous"
        IM = "intramuscular", "Intramuscular"
        ID = "intradermal", "Intradermal"
        IT = "intratracheal", "Intratracheal"

    class CargoType(models.TextChoices):
        MRNA = "mRNA", "mRNA"
        SIRNA = "siRNA", "siRNA"
        PDNA = "pDNA", "pDNA"

    experiment_id = models.CharField(max_length=100, unique=True, db_index=True)

    # Biological model
    model_name = models.CharField(max_length=100, db_index=True, help_text="e.g. HeLa, Mouse_B6")
    model_type = models.CharField(max_length=20, choices=ModelType.choices)
    model_target = models.CharField(max_length=200, blank=True, default="")

    # Delivery
    route = models.CharField(max_length=30, choices=Route.choices, default=Route.IN_VITRO)
    cargo = models.CharField(max_length=20, choices=CargoType.choices)
    cargo_type = models.CharField(max_length=200, blank=True, default="", help_text="Specific cargo name")
    dose_ug = models.FloatField(null=True, blank=True, help_text="Dose in ug nucleic acid")

    # Publication
    publication_link = models.URLField(blank=True, default="")
    publication_pmid = models.CharField(max_length=20, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.experiment_id} ({self.model_name}/{self.cargo})"


class ExperimentResult(models.Model):
    """Single measurement from an LNP experiment.
    Maps to one row in LNPDB. 19,797 total records.
    """

    class Method(models.TextChoices):
        LUMINESCENCE_NORM = "luminescence_normalized", "Luminescence (Normalized)"
        LUMINESCENCE_DISC = "luminescence_discretized_normalized", "Luminescence (Discretized)"
        LUMINESCENCE_REL = "luminescence_relative_to_Spikevax", "Luminescence (vs Spikevax)"
        PROTEIN = "protein_adundance_normalized", "Protein Abundance"
        UPTAKE = "uptake", "Cellular Uptake"
        EDITING = "editing_efficiency_normalized", "Gene Editing Efficiency"
        LRP6_KD = "LRP6_knockdown_normalized", "LRP6 Knockdown"
        DIAMETER = "diameter", "Particle Diameter (nm)"
        ZETA = "zeta_potential", "Zeta Potential (mV)"
        HEMOLYSIS = "hemolysis_percent", "Hemolysis (%)"

    lnp_id = models.CharField(max_length=50, unique=True, db_index=True, help_text="LNPDB LNP_ID")
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="results")
    formulation = models.ForeignKey("formulations.LNPFormulation", on_delete=models.CASCADE, related_name="results")

    method = models.CharField(max_length=60, choices=Method.choices, db_index=True)
    batching = models.CharField(max_length=200, blank=True, default="")
    value = models.FloatField(help_text="Measured experimental value")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["method", "value"]),
        ]

    def __str__(self):
        return f"{self.lnp_id}: {self.method}={self.value:.3f}"
