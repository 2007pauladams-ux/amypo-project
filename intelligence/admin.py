from django.contrib import admin
from .models import Category, TrendingTopic, NewsArticle, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_code', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(TrendingTopic)
class TrendingTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'velocity_percentage', 'trend_direction', 'volume_mentions', 'sentiment', 'is_hot')
    list_filter = ('sentiment', 'trend_direction', 'is_hot', 'category')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'source_name', 'published_at', 'impact_score', 'sentiment', 'is_featured', 'is_breaking')
    list_filter = ('category', 'sentiment', 'is_featured', 'is_breaking')
    search_fields = ('title', 'summary', 'content', 'source_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')
