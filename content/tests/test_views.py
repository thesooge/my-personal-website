import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from content.models import Category, ContactMessage, Post, Project


@pytest.mark.django_db
def test_home_page(client):
    resp = client.get(reverse("content:home"))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_blog_list_and_detail(client):
    user = User.objects.create_user(username="author")
    cat = Category.objects.create(name="General", slug="general")
    post = Post.objects.create(title="Post A", summary="sum", body_md="Hello", author=user, category=cat, is_published=True)
    resp = client.get(reverse("content:post_list"))
    assert resp.status_code == 200
    resp2 = client.get(reverse("content:post_detail", kwargs={"slug": post.slug}))
    assert resp2.status_code == 200


@pytest.mark.django_db
def test_projects_list_and_detail(client):
    project = Project.objects.create(name="Proj", short_description="s", body_md="Body", is_published=True)
    resp = client.get(reverse("content:project_list"))
    assert resp.status_code == 200
    resp2 = client.get(reverse("content:project_detail", kwargs={"slug": project.slug}))
    assert resp2.status_code == 200


@pytest.mark.django_db
def test_search(client):
    resp = client.get(reverse("content:search"), {"q": "hello"})
    assert resp.status_code == 200


@pytest.mark.django_db
def test_contact_form(client):
    resp = client.get(reverse("content:contact"))
    assert resp.status_code == 200
    resp2 = client.post(reverse("content:contact"), {"name": "A", "email": "a@example.com", "message": "hello world"})
    # name too short
    assert resp2.status_code == 200
    resp3 = client.post(reverse("content:contact"), {"name": "Alice", "email": "a@example.com", "message": "hello world message"})
    assert resp3.status_code == 302 