"""API endpoints for the content app."""

from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Category, Post, Project, Tag


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    posts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "posts_count", "created_at"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    
    posts_count = serializers.ReadOnlyField()
    projects_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "posts_count", "projects_count", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model."""
    
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "body_html",
            "hero_image",
            "published_at",
            "category",
            "tags",
            "author",
            "reading_time",
            "created_at",
        ]
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "body_html",
            "repo_url",
            "live_url",
            "is_featured",
            "sort_order",
            "published_at",
            "tags",
            "created_at",
        ]
        read_only_fields = fields


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Category model."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Tag model."""
    
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Post model."""
    
    queryset = Post.objects.filter(is_published=True).select_related(
        "category", "author"
    ).prefetch_related("tags")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    ordering = ["-published_at", "-created_at"]
    
    def get_queryset(self):
        """Get filtered posts."""
        queryset = super().get_queryset()
        
        # Category filter
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Tag filter
        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Search
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                summary__icontains=search
            )
        
        return queryset.distinct()


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Project model."""
    
    queryset = Project.objects.filter(is_published=True).prefetch_related(
        "tags", "images"
    )
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    ordering = ["sort_order", "-published_at", "-created_at"]
    
    def get_queryset(self):
        """Get filtered projects."""
        queryset = super().get_queryset()
        
        # Tag filter
        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Featured filter
        featured = self.request.query_params.get("featured")
        if featured is not None:
            featured_bool = featured.lower() == "true"
            queryset = queryset.filter(is_featured=featured_bool)
        
        # Search
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                name__icontains=search
            ) | queryset.filter(
                short_description__icontains=search
            )
        
        return queryset.distinct() 