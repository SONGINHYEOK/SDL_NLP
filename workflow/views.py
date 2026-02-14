import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import WorkflowRun, WorkflowStep
from .forms import WorkflowCreateForm
from .pipeline import execute_step
from equipment.models import Equipment

logger = logging.getLogger(__name__)


# ──────────────────────── Existing views ────────────────────────

@login_required
def pipeline(request):
    """Closed-loop workflow dashboard."""
    runs = WorkflowRun.objects.prefetch_related("steps").all()[:20]
    ctx = {"runs": runs}
    return render(request, "workflow/pipeline.html", ctx)


@login_required
def run_detail(request, pk):
    run = get_object_or_404(WorkflowRun.objects.prefetch_related("steps", "steps__equipment"), pk=pk)
    return render(request, "workflow/run_detail.html", {"run": run})


# ──────────────────────── Create ────────────────────────

STEP_DEFINITIONS = [
    ("design", "AI Design"),
    ("synthesize", "Synthesize"),
    ("formulate", "Formulate"),
    ("analyze", "Analyze"),
    ("learn", "Learn (Retrain)"),
]

STEP_EQUIPMENT_MAP = {
    "synthesize": "liquid_handler",
    "formulate": "microfluidic",
    "analyze": "dls",
}


@login_required
def create_run(request):
    if request.method == "POST":
        form = WorkflowCreateForm(request.POST)
        if form.is_valid():
            run = WorkflowRun.objects.create(
                name=form.cleaned_data["name"],
                description=form.cleaned_data.get("description", ""),
                ai_model=form.cleaned_data.get("ai_model"),
                status=WorkflowRun.Status.RUNNING,
                created_by=request.user,
            )
            for i, (step_type, _label) in enumerate(STEP_DEFINITIONS, start=1):
                eq = None
                eq_type = STEP_EQUIPMENT_MAP.get(step_type)
                if eq_type:
                    eq = Equipment.objects.filter(equipment_type=eq_type).first()
                status = WorkflowStep.Status.AWAITING_APPROVAL if i == 1 else WorkflowStep.Status.PENDING
                WorkflowStep.objects.create(
                    workflow=run,
                    step_order=i,
                    step_type=step_type,
                    status=status,
                    equipment=eq,
                )
            return redirect("workflow:detail", pk=run.pk)
    else:
        form = WorkflowCreateForm()
    return render(request, "workflow/create.html", {"form": form, "steps": STEP_DEFINITIONS})


# ──────────────────────── Run controls ────────────────────────

@login_required
@require_POST
def pause_run(request, pk):
    run = get_object_or_404(WorkflowRun, pk=pk)
    if run.can_pause:
        run.status = WorkflowRun.Status.PAUSED
        run.save(update_fields=["status"])
        # Running step → awaiting_approval
        run.steps.filter(status=WorkflowStep.Status.RUNNING).update(status=WorkflowStep.Status.AWAITING_APPROVAL)
    return redirect("workflow:detail", pk=run.pk)


@login_required
@require_POST
def resume_run(request, pk):
    run = get_object_or_404(WorkflowRun, pk=pk)
    if run.can_resume:
        run.status = WorkflowRun.Status.RUNNING
        run.save(update_fields=["status"])
    return redirect("workflow:detail", pk=run.pk)


@login_required
@require_POST
def cancel_run(request, pk):
    run = get_object_or_404(WorkflowRun, pk=pk)
    if run.can_cancel:
        run.status = WorkflowRun.Status.CANCELLED
        run.save(update_fields=["status"])
        run.steps.exclude(status=WorkflowStep.Status.COMPLETED).update(status=WorkflowStep.Status.SKIPPED)
    return redirect("workflow:detail", pk=run.pk)


# ──────────────────────── Step controls ────────────────────────

@login_required
@require_POST
def approve_step(request, pk, step_pk):
    run = get_object_or_404(WorkflowRun, pk=pk)
    step = get_object_or_404(WorkflowStep, pk=step_pk, workflow=run)
    if step.status == WorkflowStep.Status.AWAITING_APPROVAL:
        step.status = WorkflowStep.Status.RUNNING
        step.started_at = timezone.now()
        step.save(update_fields=["status", "started_at"])
        # Ensure run is in running state
        if run.status != WorkflowRun.Status.RUNNING:
            run.status = WorkflowRun.Status.RUNNING
            run.save(update_fields=["status"])
    return redirect("workflow:detail", pk=run.pk)


@login_required
@require_POST
def reject_step(request, pk, step_pk):
    run = get_object_or_404(WorkflowRun, pk=pk)
    step = get_object_or_404(WorkflowStep, pk=step_pk, workflow=run)
    if step.status in (WorkflowStep.Status.AWAITING_APPROVAL, WorkflowStep.Status.COMPLETED, WorkflowStep.Status.FAILED):
        step.status = WorkflowStep.Status.RUNNING
        step.output_data = {}
        step.started_at = timezone.now()
        step.completed_at = None
        step.save(update_fields=["status", "output_data", "started_at", "completed_at"])
        if run.status != WorkflowRun.Status.RUNNING:
            run.status = WorkflowRun.Status.RUNNING
            run.save(update_fields=["status"])
    return redirect("workflow:detail", pk=run.pk)


@login_required
@require_POST
def simulate_step(request, pk, step_pk):
    run = get_object_or_404(WorkflowRun, pk=pk)
    step = get_object_or_404(WorkflowStep, pk=step_pk, workflow=run)
    if step.status != WorkflowStep.Status.RUNNING:
        return redirect("workflow:detail", pk=run.pk)

    try:
        step.output_data = execute_step(run, step)
        step.status = WorkflowStep.Status.COMPLETED
        step.completed_at = timezone.now()
        step.save(update_fields=["status", "completed_at", "output_data"])
    except Exception:
        logger.exception("Step %s (pk=%s) failed", step.step_type, step.pk)
        step.status = WorkflowStep.Status.FAILED
        step.completed_at = timezone.now()
        step.save(update_fields=["status", "completed_at"])
        return redirect("workflow:detail", pk=run.pk)

    # Advance: next pending step → awaiting_approval
    next_step = run.steps.filter(status=WorkflowStep.Status.PENDING).order_by("step_order").first()
    if next_step:
        next_step.status = WorkflowStep.Status.AWAITING_APPROVAL
        next_step.save(update_fields=["status"])
    else:
        # All steps done → complete the run
        if not run.steps.exclude(status__in=["completed", "skipped"]).exists():
            run.status = WorkflowRun.Status.COMPLETED
            run.completed_at = timezone.now()
            run.save(update_fields=["status", "completed_at"])

    return redirect("workflow:detail", pk=run.pk)
