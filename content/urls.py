"""URL configuration for the content app."""

from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    # Main pages
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("contact/success/", views.contact_success, name="contact_success"),
    
    # Blog
    path("blog/", views.PostListView.as_view(), name="post_list"),
    path("blog/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    
    # Categories
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    
    # Tags
    path("tag/<slug:slug>/", views.TagDetailView.as_view(), name="tag_detail"),
    
    # Projects
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),
    
    # Search
    path("search/", views.search, name="search"),
] 