from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LLMRequestViewSet, generate, metrics

router = DefaultRouter()
router.register(
    "requests",
    LLMRequestViewSet,
    basename="llm-request",
)

urlpatterns = [
    path("generate/", generate, name="generate"),
    path("metrics/", metrics, name="metrics"),
    path("", include(router.urls)),
]