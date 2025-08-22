"""Models for the content app."""

import re
from typing import Any

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from easy_thumbnails.fields import ThumbnailerImageField
from markdown import markdown
import bleach


class Category(models.Model):
    """Category model for organizing posts."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse("content:category_detail", kwargs={"slug": self.slug})
    
    def get_posts_count(self) -> int:
        return self.posts.filter(is_published=True).count()


class Tag(models.Model):
    """Tag model for categorizing posts and projects."""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse("content:tag_detail", kwargs={"slug": self.slug})
    
    def get_posts_count(self) -> int:
        return self.posts.filter(is_published=True).count()
    
    def get_projects_count(self) -> int:
        return self.projects.filter(is_published=True).count()


class Post(models.Model):
    """Blog post model."""
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    summary = models.TextField(max_length=500)
    body_md = models.TextField()
    body_html = models.TextField(blank=True)
    hero_image = ThumbnailerImageField(
        upload_to="posts/hero/",
        blank=True,
        null=True,
        help_text="Hero image for the post (1200x600 recommended)"
    )
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    reading_time = models.PositiveIntegerField(
        default=0,
        help_text="Reading time in minutes"
    )
    og_image = models.CharField(
        max_length=255,
        blank=True,
        help_text="OpenGraph image path"
    )
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="SEO title (max 60 chars)"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO description (max 160 chars)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["is_published", "published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["category"]),
        ]
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self) -> str:
        return reverse("content:post_detail", kwargs={"slug": self.slug})
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = self.summary[:160]
        
        # Set published_at if publishing for the first time
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        # Render markdown to HTML
        self.body_html = self._render_markdown()
        
        # Calculate reading time
        self.reading_time = self._calculate_reading_time()
        
        super().save(*args, **kwargs)
    
    def _render_markdown(self) -> str:
        """Render markdown to sanitized HTML."""
        # Convert markdown to HTML
        html = markdown(
            self.body_md,
            extensions=[
                "markdown.extensions.codehilite",
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
                "markdown.extensions.toc",
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "use_pygments": False,
                }
            }
        )
        
        # Sanitize HTML
        allowed_tags = [
            "p", "br", "strong", "em", "u", "h1", "h2", "h3", "h4", "h5", "h6",
            "ul", "ol", "li", "blockquote", "pre", "code", "a", "img", "table",
            "thead", "tbody", "tr", "th", "td", "hr", "div", "span"
        ]
        allowed_attributes = {
            "a": ["href", "title", "target"],
            "img": ["src", "alt", "title", "width", "height"],
            "code": ["class"],
            "pre": ["class"],
        }
        
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
    
    def _calculate_reading_time(self) -> int:
        """Calculate reading time in minutes (average 200 words per minute)."""
        word_count = len(re.findall(r"\w+", self.body_md))
        return max(1, round(word_count / 200))
    
    @property
    def is_featured(self) -> bool:
        """Check if post is featured (published and has hero image)."""
        return self.is_published and bool(self.hero_image)
    
    def get_related_posts(self, limit: int = 3) -> "models.QuerySet[Post]":
        """Get related posts based on tags and category."""
        if not self.is_published:
            return Post.objects.none()
        
        related = Post.objects.filter(
            Q(is_published=True) &
            (Q(category=self.category) | Q(tags__in=self.tags.all())) &
            ~Q(id=self.id)
        ).distinct()[:limit]
        
        return related


class Project(models.Model):
    """Project/portfolio model."""
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    body_md = models.TextField()
    body_html = models.TextField(blank=True)
    repo_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    published_at = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["sort_order", "-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["is_published", "published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["sort_order"]),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse("content:project_detail", kwargs={"slug": self.slug})
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Set published_at if publishing for the first time
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        # Render markdown to HTML
        self.body_html = self._render_markdown()
        
        super().save(*args, **kwargs)
    
    def _render_markdown(self) -> str:
        """Render markdown to sanitized HTML."""
        # Convert markdown to HTML
        html = markdown(
            self.body_md,
            extensions=[
                "markdown.extensions.codehilite",
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "use_pygments": False,
                }
            }
        )
        
        # Sanitize HTML
        allowed_tags = [
            "p", "br", "strong", "em", "u", "h1", "h2", "h3", "h4", "h5", "h6",
            "ul", "ol", "li", "blockquote", "pre", "code", "a", "img", "table",
            "thead", "tbody", "tr", "th", "td", "hr", "div", "span"
        ]
        allowed_attributes = {
            "a": ["href", "title", "target"],
            "img": ["src", "alt", "title", "width", "height"],
            "code": ["class"],
            "pre": ["class"],
        }
        
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)


class ProjectImage(models.Model):
    """Project image model for portfolio galleries."""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = ThumbnailerImageField(
        upload_to="projects/images/",
        help_text="Project image"
    )
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["sort_order", "created_at"]
    
    def __str__(self) -> str:
        return f"{self.project.name} - {self.caption or 'Image'}"
    
    def get_absolute_url(self) -> str:
        return self.image.url


class SiteSetting(models.Model):
    """Site-wide settings model (singleton)."""
    
    owner_name = models.CharField(max_length=100, default="YOUR NAME")
    tagline = models.CharField(max_length=200, default="Software Engineer & Builder")
    bio_md = models.TextField(blank=True)
    bio_html = models.TextField(blank=True)
    avatar = ThumbnailerImageField(
        upload_to="site/",
        blank=True,
        null=True,
        help_text="Profile avatar image"
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        help_text="Social media links as JSON"
    )
    contact_email = models.EmailField(default="your.email@example.com")
    analytics_snippet = models.TextField(
        blank=True,
        help_text="Google Analytics or other tracking code"
    )
    default_meta_description = models.CharField(
        max_length=160,
        default="Personal website and portfolio",
        help_text="Default meta description for pages"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
    
    def __str__(self) -> str:
        return f"Site Settings - {self.owner_name}"
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        # Render markdown bio to HTML
        if self.bio_md:
            self.bio_html = self._render_markdown()
        
        super().save(*args, **kwargs)
        
        # Clear cache when settings are updated
        cache.delete("site_settings")
    
    def _render_markdown(self) -> str:
        """Render markdown bio to sanitized HTML."""
        html = markdown(
            self.bio_md,
            extensions=["markdown.extensions.nl2br"]
        )
        
        allowed_tags = ["p", "br", "strong", "em", "u", "a"]
        allowed_attributes = {"a": ["href", "title", "target"]}
        
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
    
    @classmethod
    def get_settings(cls) -> "SiteSetting":
        """Get or create site settings (singleton pattern)."""
        settings_obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "owner_name": "YOUR NAME",
                "tagline": "Software Engineer & Builder",
                "contact_email": "your.email@example.com",
                "default_meta_description": "Personal website and portfolio",
                "social_links": {
                    "github": "https://github.com/yourusername",
                    "linkedin": "https://linkedin.com/in/yourusername",
                    "twitter": "https://twitter.com/yourusername",
                }
            }
        )
        return settings_obj


class ContactMessage(models.Model):
    """Contact form message model."""
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self) -> str:
        return f"Message from {self.name} ({self.email})"
    
    def is_rate_limited(self) -> bool:
        """Check if this IP is rate limited."""
        from django.conf import settings
        
        cache_key = f"contact_rate_limit_{self.ip_address}"
        attempts = cache.get(cache_key, 0)
        
        return attempts >= settings.CONTACT_RATE_LIMIT
