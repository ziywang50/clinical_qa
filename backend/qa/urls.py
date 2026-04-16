from django.urls import path
from .views import QAView, HealthView

urlpatterns = [
    path("qa/", QAView.as_view(), name="clinical-qa"),
    path("health/", HealthView.as_view(), name="health"),
]
