from django.contrib import admin
from .models import TrendingTopic

@admin.register(TrendingTopic)
class TrendingTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'volume_mentions', 'velocity_percentage', 'calculated_score', 'sentiment', 'trend_direction', 'is_hot', 'updated_at')
    list_filter = ('category', 'sentiment', 'trend_direction', 'is_hot')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}
