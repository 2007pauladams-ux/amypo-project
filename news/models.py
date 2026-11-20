from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class NewsCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    icon = models.CharField(max_length=50, default='cpu', help_text='Icon identifier e.g. cpu, brief, globe, trophy, orbit, film')
    color_code = models.CharField(max_length=20, default='#8b5cf6')
    badge_class = models.CharField(max_length=50, default='badge-purple')
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'News Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'icon': self.icon,
            'color_code': self.color_code,
            'badge_class': self.badge_class,
            'description': self.description,
            'article_count': self.articles.count(),
        }


class NewsSource(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, db_index=True)
    domain = models.CharField(max_length=150, blank=True)
    url = models.URLField(max_length=400, blank=True)
    badge_color = models.CharField(max_length=30, default='#38bdf8')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class NewsArticle(models.Model):
    SENTIMENT_CHOICES = [
        ('BULLISH', 'Bullish'),
        ('BEARISH', 'Bearish'),
        ('HIGH IMPACT', 'High Impact'),
        ('DEVELOPING', 'Developing'),
        ('NEUTRAL', 'Neutral'),
    ]

    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, db_index=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='articles')
    source = models.ForeignKey(NewsSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    source_name = models.CharField(max_length=120, blank=True, default='')
    source_domain = models.CharField(max_length=150, blank=True, default='')
    author = models.CharField(max_length=150, blank=True, default='')
    
    # URL constraint prevents duplicate news articles
    url = models.URLField(max_length=600, unique=True, db_index=True, help_text='Original canonical article URL')
    image_url = models.URLField(max_length=600, blank=True, default='')
    image_gradient = models.CharField(max_length=120, default='linear-gradient(135deg, #1e1b4b 0%, #311042 100%)')
    hero_pattern = models.CharField(max_length=50, default='neural-grid')

    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    summary = models.TextField(help_text='Executive summary briefing')
    content = models.TextField(help_text='Full article intelligence report')
    key_takeaways_json = models.TextField(default='[]', help_text='JSON array of strategic takeaways')
    read_time_minutes = models.IntegerField(default=4)
    impact_score = models.IntegerField(default=85, db_index=True, help_text='1-100 rating scale')
    velocity_score = models.CharField(max_length=30, default='+240% / 1h')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='HIGH IMPACT')
    
    related_topic = models.ForeignKey('trends.TrendingTopic', on_delete=models.SET_NULL, null=True, blank=True, related_name='news_articles')
    is_featured = models.BooleanField(default=False, db_index=True)
    is_breaking = models.BooleanField(default=False, db_index=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['category', '-published_at']),
            models.Index(fields=['-impact_score', '-published_at']),
            models.Index(fields=['is_featured', '-published_at']),
            models.Index(fields=['is_breaking', '-published_at']),
        ]

    def __str__(self):
        return self.title

    def get_source_display(self):
        if self.source:
            return self.source.name
        return self.source_name or 'Global Wire'

    def get_domain_display(self):
        if self.source and self.source.domain:
            return self.source.domain
        return self.source_domain or 'wire.intel'

    def get_takeaways(self):
        try:
            return json.loads(self.key_takeaways_json)
        except Exception:
            return []

    def get_time_ago(self):
        diff = timezone.now() - self.published_at
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m ago"
        elif seconds < 86400:
            return f"{int(seconds // 3600)}h ago"
        else:
            return f"{int(seconds // 86400)}d ago"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'category_id': self.category.id if self.category else None,
            'category_name': self.category.name if self.category else 'General',
            'category_slug': self.category.slug if self.category else 'general',
            'category_color': self.category.color_code if self.category else '#8b5cf6',
            'category_badge': self.category.badge_class if self.category else 'badge-purple',
            'source_name': self.get_source_display(),
            'source_domain': self.get_domain_display(),
            'author': self.author,
            'url': self.url,
            'image_url': self.image_url,
            'published_at': self.published_at.isoformat(),
            'formatted_date': self.published_at.strftime('%b %d, %Y'),
            'time_ago': self.get_time_ago(),
            'summary': self.summary,
            'content': self.content,
            'takeaways': self.get_takeaways(),
            'read_time_minutes': self.read_time_minutes,
            'impact_score': self.impact_score,
            'velocity_score': self.velocity_score,
            'sentiment': self.sentiment,
            'image_gradient': self.image_gradient,
            'hero_pattern': self.hero_pattern,
            'is_featured': self.is_featured,
            'is_breaking': self.is_breaking,
            'views_count': self.views_count,
        }


class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_articles')
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='saved_instances')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.article.title[:30]}"


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='search_history')
    query = models.CharField(max_length=255, db_index=True)
    category_filter = models.CharField(max_length=60, blank=True, default='')
    results_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"'{self.query}' ({self.results_count} results)"
