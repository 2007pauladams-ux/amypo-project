from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='cpu', help_text='Icon identifier e.g. cpu, brief, globe, activity, shield, zap, film, trophy')
    color_code = models.CharField(max_length=20, default='#8b5cf6')
    badge_class = models.CharField(max_length=50, default='badge-purple')
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
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


class TrendingTopic(models.Model):
    SENTIMENT_CHOICES = [
        ('bullish', 'Bullish Momentum'),
        ('bearish', 'Bearish Contraction'),
        ('volatile', 'High Volatility'),
        ('critical', 'Critical Breakout'),
        ('neutral', 'Steady Baseline'),
    ]

    DIRECTION_CHOICES = [
        ('up', 'Surging Up'),
        ('down', 'Cooling Down'),
        ('hot', 'Breakout Hot'),
        ('steady', 'Steady State'),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='trending_topics')
    volume_mentions = models.IntegerField(default=12000, help_text='Global signal volume count')
    velocity_percentage = models.IntegerField(default=150, help_text='Momentum change e.g. +340%')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='bullish')
    trend_direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='up')
    movement_text = models.CharField(max_length=60, default='+14 spots this week')
    article_count = models.IntegerField(default=42, help_text='Number of associated dispatches')
    is_hot = models.BooleanField(default=False)
    sparkline_data = models.CharField(max_length=200, default='30,45,40,65,70,85,95', help_text='Comma-separated numbers for sparkline visualization')
    summary = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-velocity_percentage', '-volume_mentions']

    def __str__(self):
        return f"{self.title} ({self.velocity_percentage:+d}%)"

    def get_sparkline_points(self):
        try:
            return [int(x.strip()) for x in self.sparkline_data.split(',') if x.strip()]
        except Exception:
            return [20, 35, 45, 60, 55, 75, 90]

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'category_name': self.category.name,
            'category_slug': self.category.slug,
            'category_color': self.category.color_code,
            'category_badge': self.category.badge_class,
            'volume_mentions': self.volume_mentions,
            'velocity_percentage': self.velocity_percentage,
            'sentiment': self.sentiment,
            'trend_direction': self.trend_direction,
            'movement_text': self.movement_text,
            'article_count': self.article_count,
            'is_hot': self.is_hot,
            'sparkline': self.get_sparkline_points(),
            'summary': self.summary,
        }


class NewsArticle(models.Model):
    SENTIMENT_CHOICES = [
        ('BULLISH', 'Bullish'),
        ('BEARISH', 'Bearish'),
        ('HIGH IMPACT', 'High Impact'),
        ('DEVELOPING', 'Developing'),
        ('NEUTRAL', 'Neutral'),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=260, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    source_name = models.CharField(max_length=100)
    source_domain = models.CharField(max_length=100)
    source_badge_color = models.CharField(max_length=30, default='#38bdf8')
    image_url = models.CharField(max_length=300, blank=True, default='')
    published_at = models.DateTimeField(default=timezone.now)
    summary = models.TextField(help_text='Executive summary briefing')
    content = models.TextField(help_text='Full article intelligence report')
    key_takeaways_json = models.TextField(default='[]', help_text='JSON array of 3-4 bullet takeaways')
    read_time_minutes = models.IntegerField(default=4)
    impact_score = models.IntegerField(default=85, help_text='1-100 rating scale')
    velocity_score = models.CharField(max_length=30, default='+240% / 1h')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='HIGH IMPACT')
    image_gradient = models.CharField(max_length=120, default='linear-gradient(135deg, #1e1b4b 0%, #311042 100%)')
    hero_pattern = models.CharField(max_length=50, default='neural-grid')
    related_topic = models.ForeignKey(TrendingTopic, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    is_featured = models.BooleanField(default=False, help_text='Spotlighted in hero breakthrough section')
    is_breaking = models.BooleanField(default=False, help_text='Displayed in the live breaking news ticker')
    views_count = models.IntegerField(default=1420)
    bookmarks_count = models.IntegerField(default=88)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_takeaways(self):
        try:
            return json.loads(self.key_takeaways_json)
        except Exception:
            return []

    def get_time_ago(self):
        now = timezone.now()
        diff = now - self.published_at
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
            'category_id': self.category.id,
            'category_name': self.category.name,
            'category_slug': self.category.slug,
            'category_color': self.category.color_code,
            'category_badge': self.category.badge_class,
            'source_name': self.source_name,
            'source_domain': self.source_domain,
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
            'bookmarks_count': self.bookmarks_count,
        }


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='Intelligence analyst tracking frontier trends and macroeconomic shifts.')
    preferred_categories = models.ManyToManyField(Category, blank=True, related_name='favorited_by')
    saved_articles = models.ManyToManyField(NewsArticle, blank=True, related_name='saved_by_users')
    reading_history = models.ManyToManyField(NewsArticle, blank=True, related_name='read_by_users')
    avatar_color = models.CharField(max_length=30, default='#8b5cf6')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
