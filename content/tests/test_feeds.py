import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from content.models import Category, Post


@pytest.mark.django_db
def test_rss_feed(client):
    user = User.objects.create_user(username="author")
    cat = Category.objects.create(name="General", slug="general")
    Post.objects.create(title="Post A", summary="sum", body_md="Hello", author=user, category=cat, is_published=True)
    resp = client.get("/rss/")
    assert resp.status_code == 200
    assert b"<rss" in resp.content 