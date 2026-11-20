import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.utils import timezone

from .models import NewsCategory, NewsSource, NewsArticle, SavedArticle, SearchHistory
from trends.models import TrendingTopic

def get_context_metrics():
    """Returns platform-wide live telemetry metrics."""
    total_articles = NewsArticle.objects.count()
    active_sources = NewsSource.objects.filter(is_active=True).count()
    breaking_count = NewsArticle.objects.filter(is_breaking=True).count()
    return {
        'total_articles': total_articles,
        'active_sources': active_sources,
        'breaking_count': breaking_count,
        'signals_today': 48920 + total_articles * 14,
        'grid_latency': '18ms',
    }

def index_view(request):
    """
    TRENDORA Homepage – Real-Time News and Trend Intelligence.
    Features dark navy and purple neon theme, hero section, prominent news search bar,
    trending topics, and latest headlines.
    """
    metrics = get_context_metrics()
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:8]
    if not breaking_news.exists():
        breaking_news = NewsArticle.objects.all().order_by('-published_at')[:8]

    # Hero and featured articles
    hero_article = NewsArticle.objects.filter(is_featured=True).order_by('-published_at').first()
    if not hero_article:
        hero_article = NewsArticle.objects.order_by('-published_at').first()

    featured_articles = NewsArticle.objects.filter(is_featured=True).exclude(id=hero_article.id if hero_article else None).order_by('-published_at')[:3]
    if not featured_articles.exists():
        featured_articles = NewsArticle.objects.exclude(id=hero_article.id if hero_article else None).order_by('-published_at')[:3]

    latest_articles = NewsArticle.objects.all().order_by('-published_at')[:12]
    trending_topics = TrendingTopic.objects.all().order_by('-calculated_score', '-velocity_percentage')[:6]
    categories = NewsCategory.objects.annotate(total_articles=Count('articles')).order_by('order')

    # Serialized JSON representations for instant client-side interaction
    articles_data = [a.to_dict() for a in latest_articles]
    categories_data = [c.to_dict() for c in categories]
    trending_data = [t.to_dict() for t in trending_topics]

    context = {
        'metrics': metrics,
        'breaking_news': breaking_news,
        'hero_article': hero_article,
        'featured_article': hero_article,
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
        'trending_topics': trending_topics,
        'categories': categories,
        'articles_json': json.dumps(articles_data),
        'categories_json': json.dumps(categories_data),
        'trending_json': json.dumps(trending_data),
    }
    return render(request, 'intelligence/index.html', context)


def dashboard_view(request):
    """
    TRENDORA User Dashboard – Executive Intelligence Command Center.
    Includes sidebar, news statistics, trending keywords, recently published articles,
    and category-wise news feeds.
    """
    metrics = get_context_metrics()
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    if not breaking_news.exists():
        breaking_news = NewsArticle.objects.all().order_by('-published_at')[:6]

    trending_topics = TrendingTopic.objects.all().order_by('-calculated_score', '-velocity_percentage')[:10]
    recent_articles = NewsArticle.objects.all().select_related('category', 'source').order_by('-published_at')[:8]
    categories = NewsCategory.objects.prefetch_related('articles').order_by('order')[:6]

    total_articles_count = NewsArticle.objects.count()
    high_impact_count = NewsArticle.objects.filter(impact_score__gte=85).count()
    high_impact_percentage = int((high_impact_count / max(total_articles_count, 1)) * 100) if total_articles_count else 88

    # Saved articles count for current user
    user = request.user
    saved_count = 0
    saved_slugs = []
    if user.is_authenticated:
        saved_count = SavedArticle.objects.filter(user=user).count()
        saved_slugs = list(SavedArticle.objects.filter(user=user).values_list('article__slug', flat=True))

    context = {
        'metrics': metrics,
        'breaking_news': breaking_news,
        'trending_topics': trending_topics,
        'recent_articles': recent_articles,
        'categories': categories,
        'total_articles_count': total_articles_count,
        'high_impact_percentage': high_impact_percentage,
        'saved_count': saved_count,
        'saved_slugs': saved_slugs,
    }
    return render(request, 'intelligence/dashboard.html', context)


def advanced_search_view(request):
    """
    Advanced news search interface with multi-vector filtering (keywords, category,
    source, relevance, date), interactive cards, and pagination.
    """
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    source_id = request.GET.get('source', '').strip()
    sort_by = request.GET.get('sort', 'latest').strip()
    date_filter = request.GET.get('date', 'all').strip()
    page = request.GET.get('page', 1)

    queryset = NewsArticle.objects.all().select_related('category', 'source')

    # Apply search query
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(source_name__icontains=query) |
            Q(author__icontains=query)
        )
        # Log search history
        user = request.user if request.user.is_authenticated else None
        client_ip = request.META.get('REMOTE_ADDR')
        try:
            SearchHistory.objects.create(
                user=user,
                query=query[:250],
                category_filter=category_slug[:60],
                results_count=queryset.count(),
                ip_address=client_ip
            )
        except Exception:
            pass

    # Category filter
    if category_slug and category_slug != 'all':
        queryset = queryset.filter(category__slug=category_slug)

    # Source filter
    if source_id and source_id != 'all':
        if source_id.isdigit():
            queryset = queryset.filter(source_id=int(source_id))
        else:
            queryset = queryset.filter(source__name__icontains=source_id)

    # Date filter
    now = timezone.now()
    if date_filter == 'today':
        queryset = queryset.filter(published_at__gte=now - timezone.timedelta(days=1))
    elif date_filter == 'week':
        queryset = queryset.filter(published_at__gte=now - timezone.timedelta(days=7))
    elif date_filter == 'month':
        queryset = queryset.filter(published_at__gte=now - timezone.timedelta(days=30))

    # Sorting
    if sort_by == 'impact':
        queryset = queryset.order_by('-impact_score', '-published_at')
    elif sort_by == 'velocity':
        queryset = queryset.order_by('-published_at')
    elif sort_by == 'oldest':
        queryset = queryset.order_by('published_at')
    else: # latest
        queryset = queryset.order_by('-published_at')

    # Pagination
    paginator = Paginator(queryset, 9)
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)

    all_categories = NewsCategory.objects.all().order_by('order')
    all_sources = NewsSource.objects.filter(is_active=True).order_by('name')
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]

    context = {
        'query': query,
        'category_slug': category_slug,
        'source_id': source_id,
        'sort_by': sort_by,
        'date_filter': date_filter,
        'articles': articles_page,
        'total_results': paginator.count,
        'all_categories': all_categories,
        'all_sources': all_sources,
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/search.html', context)


def saved_news_view(request):
    """
    Saved Articles page for authenticated analyst.
    """
    user = request.user
    if not user.is_authenticated:
        demo = User.objects.filter(username='demo_analyst').first()
        user = demo if demo else User.objects.first()

    saved_instances = SavedArticle.objects.filter(user=user).select_related('article', 'article__category', 'article__source').order_by('-created_at')
    saved_articles = [s.article for s in saved_instances]

    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    all_categories = NewsCategory.objects.all().order_by('order')

    context = {
        'saved_articles': saved_articles,
        'saved_count': len(saved_articles),
        'breaking_news': breaking_news,
        'all_categories': all_categories,
    }
    return render(request, 'intelligence/saved_news.html', context)


# ==============================================================================
# JSON REST / AJAX API ENDPOINTS
# ==============================================================================

@require_GET
def api_articles(request):
    """
    REST API endpoint for retrieving articles with filters, pagination, and sorting.
    GET /api/articles/?q=...&category=...&source=...&sort=...&page=1&page_size=12
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    source = request.GET.get('source', '').strip()
    sort_by = request.GET.get('sort', 'latest').strip()
    page = request.GET.get('page', 1)
    page_size = min(int(request.GET.get('page_size', 12)), 50)

    queryset = NewsArticle.objects.all().select_related('category', 'source')

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(source_name__icontains=query)
        )

    if category and category != 'all':
        queryset = queryset.filter(category__slug=category)

    if source and source != 'all':
        if source.isdigit():
            queryset = queryset.filter(source_id=int(source))
        else:
            queryset = queryset.filter(source__slug=source)

    if sort_by == 'impact':
        queryset = queryset.order_by('-impact_score', '-published_at')
    elif sort_by == 'velocity':
        queryset = queryset.order_by('-impact_score', '-published_at')
    else:
        queryset = queryset.order_by('-published_at')

    paginator = Paginator(queryset, page_size)
    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)

    articles_data = [a.to_dict() for a in page_obj.object_list]

    return JsonResponse({
        'status': 'success',
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'articles': articles_data,
    })


@require_GET
def api_article_detail(request, slug):
    """
    REST API returning full article payload for modal / drawer reader.
    GET /api/articles/<slug>/
    """
    article = get_object_or_404(NewsArticle.objects.select_related('category', 'source', 'related_topic'), slug=slug)
    NewsArticle.objects.filter(id=article.id).update(views_count=article.views_count + 1)
    return JsonResponse({
        'status': 'success',
        'article': article.to_dict(),
    })


@require_POST
def api_bookmark_toggle(request, slug):
    """
    AJAX endpoint to bookmark or unbookmark an article for current user.
    POST /api/bookmark/<slug>/
    """
    user = request.user
    if not user.is_authenticated:
        demo = User.objects.filter(username='demo_analyst').first()
        user = demo if demo else User.objects.first()

    article = get_object_or_404(NewsArticle, slug=slug)
    saved_inst = SavedArticle.objects.filter(user=user, article=article).first()

    if saved_inst:
        saved_inst.delete()
        is_saved = False
        action = 'removed'
    else:
        SavedArticle.objects.create(user=user, article=article)
        is_saved = True
        action = 'saved'

    total_saved = SavedArticle.objects.filter(user=user).count()

    return JsonResponse({
        'status': 'success',
        'action': action,
        'is_saved': is_saved,
        'slug': slug,
        'total_saved': total_saved,
    })


@require_GET
def api_user_bookmarks(request):
    """
    Returns list of bookmarked article slugs for client-side badge synchronization.
    GET /api/user-bookmarks/
    """
    user = request.user
    if not user.is_authenticated:
        demo = User.objects.filter(username='demo_analyst').first()
        user = demo if demo else User.objects.first()

    slugs = list(SavedArticle.objects.filter(user=user).values_list('article__slug', flat=True))
    return JsonResponse({
        'status': 'success',
        'count': len(slugs),
        'saved_slugs': slugs,
    })


@require_GET
def api_simulate_signal(request):
    """
    Simulates a live incoming high-velocity intelligence dispatch for user demonstration.
    GET /api/simulate-signal/
    """
    signals = [
        {
            'title': 'Frontier Photonic Interconnect Achieves 1.6 Petabit/s Coherent Bandwidth',
            'category': 'technology',
            'source': 'MIT Tech Review',
            'impact': 99,
            'velocity': '+420% / 15m',
            'sentiment': 'BULLISH',
        },
        {
            'title': 'Sovereign Wealth Funds Rebalance 8% Liquidity Toward Clean Fusion Infrastructure',
            'category': 'business',
            'source': 'Bloomberg Terminal',
            'impact': 93,
            'velocity': '+280% / 20m',
            'sentiment': 'HIGH IMPACT',
        },
        {
            'title': 'Autonomous Deep Space Observatory Registers Unprecedented Coherent Radio Pulsar',
            'category': 'science',
            'source': 'Nature Quantum Review',
            'impact': 95,
            'velocity': '+310% / 10m',
            'sentiment': 'BULLISH',
        },
    ]
    import random
    selected = random.choice(signals)
    return JsonResponse({
        'status': 'success',
        'signal': selected,
        'timestamp': timezone.now().isoformat(),
    })
