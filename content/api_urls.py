"""API URL configuration for the content app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()
router.register(r"posts", api.PostViewSet)
router.register(r"projects", api.ProjectViewSet)
router.register(r"categories", api.CategoryViewSet)
router.register(r"tags", api.TagViewSet)

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
] 