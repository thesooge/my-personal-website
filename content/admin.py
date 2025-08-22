"""Admin configuration for the content app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Category,
    ContactMessage,
    Post,
    Project,
    ProjectImage,
    SiteSetting,
    Tag,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ["name", "slug", "posts_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    
    def posts_count(self, obj: Category) -> int:
        return obj.get_posts_count()
    posts_count.short_description = "Posts"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model."""
    
    list_display = ["name", "slug", "posts_count", "projects_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at"]
    
    def posts_count(self, obj: Tag) -> int:
        return obj.get_posts_count()
    posts_count.short_description = "Posts"
    
    def projects_count(self, obj: Tag) -> int:
        return obj.get_projects_count()
    projects_count.short_description = "Projects"


class ProjectImageInline(admin.TabularInline):
    """Inline admin for ProjectImage model."""
    
    model = ProjectImage
    extra = 1
    fields = ["image", "caption", "sort_order"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""
    
    list_display = [
        "name",
        "slug",
        "is_published",
        "is_featured",
        "sort_order",
        "published_at",
        "created_at",
    ]
    list_filter = ["is_published", "is_featured", "published_at", "created_at"]
    list_editable = ["is_published", "is_featured", "sort_order"]
    search_fields = ["name", "short_description", "body_md"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["body_html", "published_at", "created_at", "updated_at"]
    inlines = [ProjectImageInline]
    fieldsets = (
        (None, {
            "fields": ("name", "slug", "short_description", "body_md")
        }),
        ("Details", {
            "fields": ("repo_url", "live_url", "tags")
        }),
        ("Publishing", {
            "fields": ("is_published", "is_featured", "sort_order", "published_at")
        }),
        ("Rendered Content", {
            "fields": ("body_html",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    actions = ["publish_projects", "unpublish_projects"]
    
    def publish_projects(self, request, queryset):
        """Action to publish selected projects."""
        from django.utils import timezone
        
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(
            request,
            f"Successfully published {updated} project(s)."
        )
    publish_projects.short_description = "Publish selected projects"
    
    def unpublish_projects(self, request, queryset):
        """Action to unpublish selected projects."""
        updated = queryset.update(is_published=False, published_at=None)
        self.message_user(
            request,
            f"Successfully unpublished {updated} project(s)."
        )
    unpublish_projects.short_description = "Unpublish selected projects"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model."""
    
    list_display = [
        "title",
        "slug",
        "author",
        "category",
        "is_published",
        "reading_time",
        "published_at",
        "created_at",
    ]
    list_filter = [
        "is_published",
        "published_at",
        "created_at",
        "category",
        "tags",
        "author",
    ]
    list_editable = ["is_published"]
    search_fields = ["title", "summary", "body_md"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = [
        "body_html",
        "reading_time",
        "published_at",
        "created_at",
        "updated_at",
    ]
    filter_horizontal = ["tags"]
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "summary", "body_md")
        }),
        ("Content", {
            "fields": ("hero_image", "category", "tags", "author")
        }),
        ("SEO", {
            "fields": ("og_image", "meta_title", "meta_description")
        }),
        ("Publishing", {
            "fields": ("is_published", "published_at")
        }),
        ("Rendered Content", {
            "fields": ("body_html",),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("reading_time", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    actions = ["publish_posts", "unpublish_posts"]
    
    def publish_posts(self, request, queryset):
        """Action to publish selected posts."""
        from django.utils import timezone
        
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(
            request,
            f"Successfully published {updated} post(s)."
        )
    publish_posts.short_description = "Publish selected posts"
    
    def unpublish_posts(self, request, queryset):
        """Action to unpublish selected posts."""
        updated = queryset.update(is_published=False, published_at=None)
        self.message_user(
            request,
            f"Successfully unpublished {updated} post(s)."
        )
    unpublish_posts.short_description = "Unpublish selected posts"


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    """Admin configuration for SiteSetting model."""
    
    def has_add_permission(self, request):
        """Only allow one site setting instance."""
        return not SiteSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of site settings."""
        return False
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("owner_name", "tagline", "bio_md", "avatar")
        }),
        ("Contact", {
            "fields": ("contact_email",)
        }),
        ("Social Media", {
            "fields": ("social_links",),
            "description": "Enter social media URLs as JSON. Example: {\"github\": \"https://github.com/username\"}"
        }),
        ("SEO & Analytics", {
            "fields": ("default_meta_description", "analytics_snippet")
        }),
        ("Rendered Bio", {
            "fields": ("bio_html",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ["bio_html", "updated_at"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin configuration for ContactMessage model."""
    
    list_display = [
        "name",
        "email",
        "ip_address",
        "created_at",
        "message_preview",
    ]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["name", "email", "message", "ip_address", "created_at"]
    
    def message_preview(self, obj: ContactMessage) -> str:
        """Show a preview of the message."""
        preview = obj.message[:100]
        if len(obj.message) > 100:
            preview += "..."
        return preview
    message_preview.short_description = "Message Preview"
    
    def has_add_permission(self, request):
        """Contact messages are created through the form only."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Contact messages are read-only."""
        return False
