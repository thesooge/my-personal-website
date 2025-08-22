"""Tailwind theme app configuration."""

from django.apps import AppConfig


class ThemeConfig(AppConfig):
    """Configuration for the Tailwind theme app."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "theme" 