import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from content.models import Category, Post, Project, Tag


@pytest.mark.django_db
def test_post_slug_and_markdown_and_reading_time():
    user = User.objects.create_user(username="author")
    cat = Category.objects.create(name="General", slug="general")
    post = Post.objects.create(
        title="Hello World",
        summary="Summary",
        body_md="# Heading\n\nSome text",
        author=user,
        category=cat,
        is_published=True,
    )
    assert post.slug == "hello-world"
    assert "<h1" in post.body_html
    assert post.reading_time >= 1
    assert post.published_at is not None


@pytest.mark.django_db
def test_project_slug_and_publish_time():
    tag = Tag.objects.create(name="Django", slug="django")
    project = Project.objects.create(
        name="My Project",
        short_description="desc",
        body_md="Body",
        is_published=True,
    )
    project.tags.add(tag)
    assert project.slug == "my-project"
    assert project.published_at is not None 