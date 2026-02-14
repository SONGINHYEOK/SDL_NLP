from django.contrib import admin
from .models import AIModel, Prediction, GeneratedCandidate
admin.site.register(AIModel)
admin.site.register(Prediction)
admin.site.register(GeneratedCandidate)
