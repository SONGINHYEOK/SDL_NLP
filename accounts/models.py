from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user with role and team."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        RESEARCHER = "researcher", "Researcher"
        OPERATOR = "operator", "Operator"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RESEARCHER)
    organization = models.CharField(max_length=200, blank=True, default="")
    bio = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
