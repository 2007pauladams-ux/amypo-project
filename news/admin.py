from django.contrib import admin
from .models import NewsCategory, NewsSource, NewsArticle, SavedArticle, SearchHistory

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'badge_class', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'domain')

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'source_name', 'impact_score', 'sentiment', 'is_featured', 'is_breaking', 'published_at')
    list_filter = ('category', 'sentiment', 'is_featured', 'is_breaking', 'published_at')
    search_fields = ('title', 'summary', 'content', 'author', 'source_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    search_fields = ('user__username', 'article__title')
    list_filter = ('created_at',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('query', 'user', 'category_filter', 'results_count', 'created_at')
    search_fields = ('query', 'user__username', 'ip_address')
    list_filter = ('created_at',)
