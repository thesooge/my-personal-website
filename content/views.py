"""Views for the content app."""

from typing import Any

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView

from .forms import ContactForm
from .models import Category, Post, Project, SiteSetting, Tag


def home(request: HttpRequest) -> HttpResponse:
    """Home page view."""
    site_settings = SiteSetting.get_settings()
    
    # Get featured posts and projects
    featured_posts = Post.objects.filter(
        is_published=True
    ).select_related("category", "author").prefetch_related("tags")[:3]
    
    featured_projects = Project.objects.filter(
        is_published=True, is_featured=True
    ).prefetch_related("tags", "images")[:3]
    
    # Get recent posts
    recent_posts = Post.objects.filter(
        is_published=True
    ).select_related("category", "author").prefetch_related("tags")[:6]
    
    context = {
        "site_settings": site_settings,
        "featured_posts": featured_posts,
        "featured_projects": featured_projects,
        "recent_posts": recent_posts,
    }
    
    return render(request, "content/home.html", context)


def about(request: HttpRequest) -> HttpResponse:
    """About page view."""
    site_settings = SiteSetting.get_settings()
    
    context = {
        "site_settings": site_settings,
    }
    
    return render(request, "content/about.html", context)


class PostListView(ListView):
    """Blog post list view with search and filtering."""
    
    model = Post
    template_name = "content/post_list.html"
    context_object_name = "posts"
    paginate_by = 10
    
    def get_queryset(self):
        """Get filtered and searched posts."""
        queryset = Post.objects.filter(
            is_published=True
        ).select_related("category", "author").prefetch_related("tags")
        
        # Search functionality
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(body_html__icontains=query)
            )
        
        # Category filter
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Tag filter
        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context["site_settings"] = SiteSetting.get_settings()
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_tag"] = self.request.GET.get("tag", "")
        return context


class PostDetailView(DetailView):
    """Blog post detail view."""
    
    model = Post
    template_name = "content/post_detail.html"
    context_object_name = "post"
    
    def get_queryset(self):
        """Get published posts only."""
        return Post.objects.filter(
            is_published=True
        ).select_related("category", "author").prefetch_related("tags")
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context["site_settings"] = SiteSetting.get_settings()
        context["related_posts"] = self.object.get_related_posts()
        return context


class CategoryDetailView(DetailView):
    """Category detail view showing all posts in a category."""
    
    model = Category
    template_name = "content/category_detail.html"
    context_object_name = "category"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add posts for this category."""
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(
            category=self.object,
            is_published=True
        ).select_related("author").prefetch_related("tags")
        
        # Pagination
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        context["posts"] = page_obj
        context["site_settings"] = SiteSetting.get_settings()
        return context


class TagDetailView(DetailView):
    """Tag detail view showing all posts and projects with a tag."""
    
    model = Tag
    template_name = "content/tag_detail.html"
    context_object_name = "tag"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add posts and projects for this tag."""
        context = super().get_context_data(**kwargs)
        
        # Get posts with this tag
        posts = Post.objects.filter(
            tags=self.object,
            is_published=True
        ).select_related("category", "author").prefetch_related("tags")
        
        # Get projects with this tag
        projects = Project.objects.filter(
            tags=self.object,
            is_published=True
        ).prefetch_related("tags", "images")
        
        context["posts"] = posts[:5]  # Show only 5 most recent posts
        context["projects"] = projects
        context["site_settings"] = SiteSetting.get_settings()
        return context


class ProjectListView(ListView):
    """Project list view with filtering."""
    
    model = Project
    template_name = "content/project_list.html"
    context_object_name = "projects"
    paginate_by = 12
    
    def get_queryset(self):
        """Get published projects with optional filtering."""
        queryset = Project.objects.filter(
            is_published=True
        ).prefetch_related("tags", "images")
        
        # Tag filter
        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context["site_settings"] = SiteSetting.get_settings()
        context["tags"] = Tag.objects.all()
        context["selected_tag"] = self.request.GET.get("tag", "")
        return context


class ProjectDetailView(DetailView):
    """Project detail view."""
    
    model = Project
    template_name = "content/project_detail.html"
    context_object_name = "project"
    
    def get_queryset(self):
        """Get published projects only."""
        return Project.objects.filter(
            is_published=True
        ).prefetch_related("tags", "images")
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context["site_settings"] = SiteSetting.get_settings()
        return context


@require_http_methods(["GET", "POST"])
def contact(request: HttpRequest) -> HttpResponse:
    """Contact form view with rate limiting."""
    site_settings = SiteSetting.get_settings()
    
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Check rate limiting
            ip_address = request.META.get("REMOTE_ADDR", "")
            cache_key = f"contact_rate_limit_{ip_address}"
            attempts = cache.get(cache_key, 0)
            
            if attempts >= settings.CONTACT_RATE_LIMIT:
                messages.error(
                    request,
                    "Too many contact attempts. Please try again later."
                )
                return redirect("content:contact")
            
            # Save the message
            message = form.save(commit=False)
            message.ip_address = ip_address
            message.save()
            
            # Increment rate limit counter
            cache.set(
                cache_key,
                attempts + 1,
                settings.CONTACT_RATE_LIMIT_WINDOW
            )
            
            messages.success(
                request,
                "Thank you for your message! I'll get back to you soon."
            )
            return redirect("content:contact_success")
    else:
        form = ContactForm()
    
    context = {
        "form": form,
        "site_settings": site_settings,
    }
    
    return render(request, "content/contact.html", context)


def contact_success(request: HttpRequest) -> HttpResponse:
    """Contact form success page."""
    site_settings = SiteSetting.get_settings()
    
    context = {
        "site_settings": site_settings,
    }
    
    return render(request, "content/contact_success.html", context)


def search(request: HttpRequest) -> HttpResponse:
    """Search functionality across posts and projects."""
    query = request.GET.get("q", "")
    site_settings = SiteSetting.get_settings()
    
    if not query:
        return redirect("content:home")
    
    # Search in posts
    posts = Post.objects.filter(
        Q(is_published=True) &
        (Q(title__icontains=query) |
         Q(summary__icontains=query) |
         Q(body_html__icontains=query))
    ).select_related("category", "author").prefetch_related("tags")
    
    # Search in projects
    projects = Project.objects.filter(
        Q(is_published=True) &
        (Q(name__icontains=query) |
         Q(short_description__icontains=query) |
         Q(body_html__icontains=query))
    ).prefetch_related("tags", "images")
    
    # Pagination for posts
    post_paginator = Paginator(posts, 10)
    post_page = request.GET.get("post_page", 1)
    post_page_obj = post_paginator.get_page(post_page)
    
    # Pagination for projects
    project_paginator = Paginator(projects, 12)
    project_page = request.GET.get("project_page", 1)
    project_page_obj = project_paginator.get_page(project_page)
    
    context = {
        "query": query,
        "posts": post_page_obj,
        "projects": project_page_obj,
        "site_settings": site_settings,
        "posts_count": posts.count(),
        "projects_count": projects.count(),
    }
    
    return render(request, "content/search.html", context)
