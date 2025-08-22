"""Context processors for the content app."""

from django.core.cache import cache

from .models import SiteSetting


def site_settings(request):
    """Make site settings available in all templates."""
    # Try to get from cache first
    settings_obj = cache.get("site_settings")
    
    if not settings_obj:
        # Get or create site settings
        settings_obj = SiteSetting.get_settings()
        # Cache for 1 hour
        cache.set("site_settings", settings_obj, 3600)
    
    return {"site_settings": settings_obj} 