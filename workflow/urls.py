from django.urls import path
from . import views

app_name = "workflow"
urlpatterns = [
    path("", views.pipeline, name="pipeline"),
    path("create/", views.create_run, name="create_run"),
    path("<int:pk>/", views.run_detail, name="detail"),
    path("<int:pk>/pause/", views.pause_run, name="pause_run"),
    path("<int:pk>/resume/", views.resume_run, name="resume_run"),
    path("<int:pk>/cancel/", views.cancel_run, name="cancel_run"),
    path("<int:pk>/step/<int:step_pk>/approve/", views.approve_step, name="approve_step"),
    path("<int:pk>/step/<int:step_pk>/reject/", views.reject_step, name="reject_step"),
    path("<int:pk>/step/<int:step_pk>/simulate/", views.simulate_step, name="simulate_step"),
]
