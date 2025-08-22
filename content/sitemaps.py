"""Sitemaps for the content app."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post, Project


class PostSitemap(Sitemap):
    """Sitemap for blog posts."""
    
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        """Get published posts."""
        return Post.objects.filter(is_published=True)
    
    def lastmod(self, obj: Post):
        """Get the last modification date."""
        return obj.updated_at
    
    def location(self, obj: Post) -> str:
        """Get the URL for the post."""
        return obj.get_absolute_url()


class ProjectSitemap(Sitemap):
    """Sitemap for projects."""
    
    changefreq = "monthly"
    priority = 0.7
    
    def items(self):
        """Get published projects."""
        return Project.objects.filter(is_published=True)
    
    def lastmod(self, obj: Project):
        """Get the last modification date."""
        return obj.updated_at
    
    def location(self, obj: Project) -> str:
        """Get the URL for the project."""
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        """Get static page names."""
        return ["content:home", "content:about", "content:post_list", "content:project_list", "content:contact"]
    
    def location(self, item: str) -> str:
        """Get the URL for the static page."""
        return reverse(item) 