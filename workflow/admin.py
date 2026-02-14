from django.contrib import admin
from .models import WorkflowRun, WorkflowStep
admin.site.register(WorkflowRun)
admin.site.register(WorkflowStep)
