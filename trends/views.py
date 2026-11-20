from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import TrendingTopic
from news.models import NewsCategory, NewsArticle

def trending_topics_view(request):
    """
    Dedicated Trending Topics page for TRENDORA.
    Displays trending topics across Technology, Business, Politics, Sports, Science,
    and Entertainment with momentum indicators, article counts, and sparklines.
    """
    cat_slug = request.GET.get('category', '').strip()
    queryset = TrendingTopic.objects.all().select_related('category')

    if cat_slug and cat_slug != 'all':
        queryset = queryset.filter(category__slug=cat_slug)

    all_trends = queryset.order_by('-calculated_score', '-velocity_percentage')
    hot_trends = TrendingTopic.objects.filter(is_hot=True).select_related('category').order_by('-velocity_percentage')[:4]
    categories = NewsCategory.objects.all().order_by('order')
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]

    context = {
        'trending_topics': all_trends,
        'all_trends': all_trends,
        'hot_trends': hot_trends,
        'categories': categories,
        'selected_category': cat_slug,
        'breaking_news': breaking_news,
        'total_trends_count': all_trends.count(),
    }
    return render(request, 'intelligence/trending.html', context)


@require_GET
def api_trending_topics(request):
    """
    REST API endpoint returning ranked trending topics.
    GET /api/trends/?category=...&limit=20
    """
    cat_slug = request.GET.get('category', '').strip()
    limit = min(int(request.GET.get('limit', 20)), 100)

    queryset = TrendingTopic.objects.all().select_related('category')
    if cat_slug and cat_slug != 'all':
        queryset = queryset.filter(category__slug=cat_slug)

    topics = queryset.order_by('-calculated_score', '-velocity_percentage')[:limit]
    data = [t.to_dict() for t in topics]

    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'trends': data,
    })
