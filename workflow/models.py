from django.db import models
from django.conf import settings


class WorkflowRun(models.Model):
    """One cycle of the closed-loop optimization pipeline."""

    class Status(models.TextChoices):
        DESIGNING = "designing", "Designing"
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        ANALYZING = "analyzing", "Analyzing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DESIGNING)
    iteration = models.IntegerField(default=1, help_text="Current optimization cycle")

    ai_model = models.ForeignKey(
        "ai_models.AIModel", on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_runs"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_runs"
    )

    report_text = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} (Iter {self.iteration}, {self.status})"

    @property
    def progress_pct(self):
        total = self.steps.count()
        if total == 0:
            return 0
        done = self.steps.filter(status="completed").count()
        return int(done / total * 100)

    @property
    def current_step(self):
        step = self.steps.exclude(status__in=["completed", "skipped"]).order_by("step_order").first()
        return step

    @property
    def can_pause(self):
        return self.status in (self.Status.RUNNING,)

    @property
    def can_resume(self):
        return self.status in (self.Status.PAUSED,)

    @property
    def can_cancel(self):
        return self.status in (self.Status.RUNNING, self.Status.PAUSED, self.Status.DESIGNING, self.Status.QUEUED)


class WorkflowStep(models.Model):
    """Individual step in a workflow run."""

    class StepType(models.TextChoices):
        DESIGN = "design", "AI Design"
        SYNTHESIZE = "synthesize", "Synthesize"
        FORMULATE = "formulate", "Formulate"
        ANALYZE = "analyze", "Analyze"
        LEARN = "learn", "Learn (Retrain)"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"
        AWAITING_APPROVAL = "awaiting_approval", "Awaiting Approval"

    workflow = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name="steps")
    step_order = models.IntegerField()
    step_type = models.CharField(max_length=20, choices=StepType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)

    equipment = models.ForeignKey(
        "equipment.Equipment", on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_steps"
    )

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["workflow", "step_order"]
        unique_together = ["workflow", "step_order"]

    def __str__(self):
        return f"Step {self.step_order}: {self.get_step_type_display()} ({self.status})"
