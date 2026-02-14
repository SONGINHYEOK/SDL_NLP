from django.urls import path
from . import views

app_name = "assistant"

urlpatterns = [
    path("api/chat/", views.chat_api, name="chat_api"),
    path("api/report/<int:pk>/", views.generate_report, name="generate_report"),
]
