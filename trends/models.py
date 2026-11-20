from django.db import models
from django.utils import timezone
import json

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

    title = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=160, unique=True, db_index=True)
    category = models.ForeignKey('news.NewsCategory', on_delete=models.CASCADE, related_name='trending_topics')
    volume_mentions = models.IntegerField(default=12000, help_text='Global signal volume count')
    velocity_percentage = models.IntegerField(default=150, help_text='Momentum change e.g. +340%')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='bullish')
    trend_direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='up')
    movement_text = models.CharField(max_length=80, default='+14 spots this week')
    article_count = models.IntegerField(default=0, help_text='Number of associated dispatches')
    is_hot = models.BooleanField(default=False, db_index=True)
    sparkline_data = models.CharField(max_length=200, default='30,45,40,65,70,85,95')
    summary = models.CharField(max_length=255, blank=True)
    calculated_score = models.FloatField(default=0.0, db_index=True, help_text='Algorithmic trend score based on frequency and recency')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-velocity_percentage', '-volume_mentions']
        indexes = [
            models.Index(fields=['-calculated_score']),
            models.Index(fields=['-velocity_percentage']),
            models.Index(fields=['category', '-calculated_score']),
        ]

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
            'category_name': self.category.name if self.category else 'General',
            'category_slug': self.category.slug if self.category else 'general',
            'category_color': self.category.color_code if self.category else '#8b5cf6',
            'category_badge': self.category.badge_class if self.category else 'badge-purple',
            'volume_mentions': self.volume_mentions,
            'velocity_percentage': self.velocity_percentage,
            'sentiment': self.sentiment,
            'trend_direction': self.trend_direction,
            'movement_text': self.movement_text,
            'article_count': self.article_count,
            'is_hot': self.is_hot,
            'calculated_score': round(self.calculated_score, 2),
            'sparkline': self.get_sparkline_points(),
            'summary': self.summary,
        }
