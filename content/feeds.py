"""RSS feeds for the content app."""

from django.contrib.syndication.views import Feed
from django.urls import path, reverse_lazy
from django.utils.feedgenerator import Rss201rev2Feed, Enclosure

from .models import Post


class LatestPostsFeed(Feed):
    """RSS feed for latest blog posts."""
    
    title = "Latest Blog Posts"
    link = reverse_lazy("content:post_list")
    description = "Latest blog posts and articles"
    feed_type = Rss201rev2Feed
    
    def items(self):
        """Get the latest published posts."""
        return Post.objects.filter(
            is_published=True
        ).select_related("category", "author")[:20]
    
    def item_title(self, item: Post) -> str:
        """Get the title for each item."""
        return item.title
    
    def item_description(self, item: Post) -> str:
        """Get the description for each item."""
        return item.summary
    
    def item_link(self, item: Post) -> str:
        """Get the link for each item."""
        return item.get_absolute_url()
    
    def item_author_name(self, item: Post) -> str:
        """Get the author name for each item."""
        return item.author.get_full_name() or item.author.username
    
    def item_pubdate(self, item: Post):
        """Get the publication date for each item."""
        return item.published_at
    
    def item_categories(self, item: Post) -> list[str]:
        """Get the categories for each item."""
        categories = []
        if item.category:
            categories.append(item.category.name)
        return categories
    
    def item_enclosures(self, item: Post):
        """Get the hero image as an enclosure if available."""
        if item.hero_image:
            length = getattr(item.hero_image, "size", 0)
            return [Enclosure(url=item.hero_image.url, length=str(length), mime_type="image/jpeg")]
        return []


urlpatterns = [
    path("", LatestPostsFeed(), name="rss"),
] 