import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from content.models import Category, Post, Project


@pytest.mark.django_db
def test_posts_api(client):
    user = User.objects.create_user(username="author")
    cat = Category.objects.create(name="General", slug="general")
    Post.objects.create(title="Post A", summary="sum", body_md="Hello", author=user, category=cat, is_published=True)
    resp = client.get("/api/posts/")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


@pytest.mark.django_db
def test_projects_api(client):
    Project.objects.create(name="Proj", short_description="s", body_md="Body", is_published=True)
    resp = client.get("/api/projects/")
    assert resp.status_code == 200 