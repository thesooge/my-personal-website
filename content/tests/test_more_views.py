import io
import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image

from content.models import Category, Post, Project, Tag, SiteSetting
from content.sitemaps import PostSitemap, ProjectSitemap


def make_image_file(name="test.jpg", size=(50, 50), color=(255, 0, 0)):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, "JPEG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/jpeg")


@pytest.mark.django_db
def test_category_and_tag_pages(client):
    user = User.objects.create_user(username="u1")
    cat = Category.objects.create(name="Cat", slug="cat")
    tag = Tag.objects.create(name="T1", slug="t1")
    p = Post.objects.create(title="T", summary="S", body_md="B", author=user, category=cat, is_published=True)
    p.tags.add(tag)
    resp1 = client.get(reverse("content:category_detail", kwargs={"slug": cat.slug}))
    assert resp1.status_code == 200
    resp2 = client.get(reverse("content:tag_detail", kwargs={"slug": tag.slug}))
    assert resp2.status_code == 200


@pytest.mark.django_db
def test_blog_filters_and_search(client):
    user = User.objects.create_user(username="u2")
    cat = Category.objects.create(name="FilterCat", slug="filter-cat")
    tag = Tag.objects.create(name="FilterTag", slug="filter-tag")
    p = Post.objects.create(title="Filter Post", summary="sum", body_md="hello world", author=user, category=cat, is_published=True)
    p.tags.add(tag)
    resp = client.get(reverse("content:post_list"), {"q": "hello"})
    assert resp.status_code == 200
    resp = client.get(reverse("content:post_list"), {"category": cat.slug})
    assert resp.status_code == 200
    resp = client.get(reverse("content:post_list"), {"tag": tag.slug})
    assert resp.status_code == 200


@pytest.mark.django_db
def test_projects_filter_and_detail(client):
    t = Tag.objects.create(name="PTag", slug="ptag")
    proj = Project.objects.create(name="Proj1", short_description="desc", body_md="body", is_published=True)
    proj.tags.add(t)
    resp = client.get(reverse("content:project_list"), {"tag": t.slug})
    assert resp.status_code == 200


@pytest.mark.django_db
def test_contact_rate_limit(client, settings):
    settings.CONTACT_RATE_LIMIT = 1
    settings.CONTACT_RATE_LIMIT_WINDOW = 60
    # first OK
    resp1 = client.post(reverse("content:contact"), {"name": "Alice", "email": "a@example.com", "message": "hello world"})
    assert resp1.status_code == 302
    # second should be rate limited
    resp2 = client.post(reverse("content:contact"), {"name": "Alice", "email": "a@example.com", "message": "hello again"}, follow=True)
    assert resp2.status_code == 200


@pytest.mark.django_db
def test_feed_enclosure_with_image(client):
    user = User.objects.create_user(username="u3")
    cat = Category.objects.create(name="C3", slug="c3")
    img = make_image_file()
    post = Post.objects.create(title="With Image", summary="S", body_md="B", author=user, category=cat, is_published=True, hero_image=img)
    resp = client.get("/rss/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_sitemap_helpers():
    user = User.objects.create_user(username="u4")
    cat = Category.objects.create(name="C4", slug="c4")
    post = Post.objects.create(title="S1", summary="S", body_md="B", author=user, category=cat, is_published=True)
    proj = Project.objects.create(name="P1", short_description="s", body_md="b", is_published=True)
    ps = PostSitemap()
    assert ps.location(post) == post.get_absolute_url()
    assert ps.lastmod(post) == post.updated_at
    prs = ProjectSitemap()
    assert prs.location(proj) == proj.get_absolute_url()
    assert prs.lastmod(proj) == proj.updated_at


@pytest.mark.django_db
def test_sitesetting_get_settings_cached():
    s = SiteSetting.get_settings()
    assert s.owner_name
    # call again to hit cache path
    s2 = SiteSetting.get_settings()
    assert s2.pk == s.pk 