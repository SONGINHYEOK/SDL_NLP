from django.db import models


class AIModel(models.Model):
    """Trained ML model for LNP property prediction, structure generation, etc."""

    class ModelType(models.TextChoices):
        PROPERTY_PREDICTOR = "property_predictor", "Property Predictor"
        STRUCTURE_GENERATOR = "structure_generator", "Structure Generator"
        FORMULATION_OPTIMIZER = "formulation_optimizer", "Formulation Optimizer"
        EXPERIMENT_DESIGNER = "experiment_designer", "Experiment Designer"

    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, default="1.0")
    model_type = models.CharField(max_length=30, choices=ModelType.choices)
    description = models.TextField(blank=True, default="")

    # Model performance
    metrics = models.JSONField(default=dict, blank=True, help_text="{'r2': 0.85, 'rmse': 0.12}")
    training_data_count = models.IntegerField(default=0)

    # Storage
    model_path = models.CharField(max_length=500, blank=True, default="")
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ["name", "version"]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()})"


class Prediction(models.Model):
    """AI model prediction record."""
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name="predictions")
    formulation = models.ForeignKey(
        "formulations.LNPFormulation", on_delete=models.SET_NULL, null=True, blank=True, related_name="predictions"
    )
    input_data = models.JSONField(help_text="Model input features")
    output_data = models.JSONField(help_text="Predicted values")
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pred#{self.pk} by {self.ai_model.name}"


class GeneratedCandidate(models.Model):
    """AI-generated lipid candidate for closed-loop optimization."""

    class Status(models.TextChoices):
        GENERATED = "generated", "Generated"
        SELECTED = "selected", "Selected"
        SYNTHESIZED = "synthesized", "Synthesized"
        TESTED = "tested", "Tested"
        VALIDATED = "validated", "Validated"
        REJECTED = "rejected", "Rejected"

    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name="candidates")
    generation = models.IntegerField(default=1, help_text="Iteration number in evolutionary optimization")

    smiles = models.TextField()
    predicted_properties = models.JSONField(default=dict)

    # Multi-objective scores
    efficacy_score = models.FloatField(null=True, blank=True)
    stability_score = models.FloatField(null=True, blank=True)
    safety_score = models.FloatField(null=True, blank=True)
    pareto_rank = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.GENERATED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["pareto_rank", "-efficacy_score"]

    def __str__(self):
        return f"Gen{self.generation}-{self.pk} ({self.status})"
