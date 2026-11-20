from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import random
import re

from .models import Category, TrendingTopic, NewsArticle, UserProfile

# ==============================================================================
# 1. HOMEPAGE VIEW
# ==============================================================================
def index(request):
    """
    Renders the primary TRENDORA Real-Time News and Trend Intelligence homepage.
    """
    categories = Category.objects.annotate(total_articles=Count('articles')).order_by('order', 'name')
    trending_topics = TrendingTopic.objects.select_related('category').order_by('-velocity_percentage')[:6]
    
    # Featured story
    featured_article = NewsArticle.objects.filter(is_featured=True).first()
    if not featured_article:
        featured_article = NewsArticle.objects.first()

    # Breaking news for ticker
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:8]
    if not breaking_news.exists():
        breaking_news = NewsArticle.objects.order_by('-published_at')[:6]

    # Latest headline intelligence
    latest_articles = NewsArticle.objects.select_related('category', 'related_topic').order_by('-published_at')

    # Telemetry statistics
    total_signals = 482920
    active_clusters = 1418
    sentiment_bullish = 74.2
    avg_latency = 18

    # Embedded JSON for instant client-side interactions
    articles_json = json.dumps([a.to_dict() for a in latest_articles])
    categories_json = json.dumps([c.to_dict() for c in categories])
    trending_json = json.dumps([t.to_dict() for t in trending_topics])

    context = {
        'categories': categories,
        'trending_topics': trending_topics,
        'featured_article': featured_article,
        'breaking_news': breaking_news,
        'latest_articles': latest_articles,
        'articles_json': articles_json,
        'categories_json': categories_json,
        'trending_json': trending_json,
        'stats': {
            'total_signals': f"{total_signals:,}",
            'active_clusters': f"{active_clusters:,}",
            'sentiment_bullish': f"{sentiment_bullish}%",
            'avg_latency': f"{avg_latency}ms",
        }
    }
    return render(request, 'intelligence/index.html', context)


# ==============================================================================
# 2. USER DASHBOARD VIEW
# ==============================================================================
def dashboard(request):
    """
    Renders the comprehensive TRENDORA Analyst Dashboard.
    Includes news stats, trending keywords, recent articles, and category-wise sections.
    """
    categories = Category.objects.prefetch_related('articles').all().order_by('order')
    trending_topics = TrendingTopic.objects.select_related('category').order_by('-velocity_percentage')[:10]
    recent_articles = NewsArticle.objects.select_related('category', 'related_topic').order_by('-published_at')[:6]
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]

    total_articles = NewsArticle.objects.count()
    high_impact_count = NewsArticle.objects.filter(impact_score__gte=90).count()
    high_impact_percentage = int((high_impact_count / total_articles * 100)) if total_articles > 0 else 85

    context = {
        'categories': categories,
        'trending_topics': trending_topics,
        'recent_articles': recent_articles,
        'breaking_news': breaking_news,
        'total_articles_count': total_articles,
        'high_impact_percentage': high_impact_percentage,
    }
    return render(request, 'intelligence/dashboard.html', context)


# ==============================================================================
# 3. ADVANCED SEARCH VIEW
# ==============================================================================
def advanced_search(request):
    """
    Renders the Advanced News Search Interface with category, date, source and sort filters.
    """
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', 'all').strip()
    date_filter = request.GET.get('date', 'all').strip()
    source_filter = request.GET.get('source', 'all').strip()
    sort_filter = request.GET.get('sort', 'relevance').strip()

    articles = NewsArticle.objects.select_related('category', 'related_topic').all()

    # Query Filter
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(source_name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Category Filter
    if category_slug and category_slug != 'all':
        articles = articles.filter(category__slug=category_slug)

    # Date Filter
    now = timezone.now()
    if date_filter == 'today':
        articles = articles.filter(published_at__gte=now - timedelta(days=1))
    elif date_filter == 'week':
        articles = articles.filter(published_at__gte=now - timedelta(days=7))
    elif date_filter == 'month':
        articles = articles.filter(published_at__gte=now - timedelta(days=30))

    # Source Filter
    if source_filter and source_filter != 'all':
        articles = articles.filter(source_name__iexact=source_filter)

    # Sort Filter
    if sort_filter == 'latest':
        articles = articles.order_by('-published_at')
    elif sort_filter == 'velocity':
        articles = articles.order_by('-views_count', '-published_at')
    else: # relevance / impact
        articles = articles.order_by('-impact_score', '-published_at')

    categories = Category.objects.all().order_by('order')
    sources = list(NewsArticle.objects.values_list('source_name', flat=True).distinct())
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]

    articles_json = json.dumps([a.to_dict() for a in articles])

    context = {
        'articles': articles,
        'articles_json': articles_json,
        'categories': categories,
        'sources': sources,
        'query': query,
        'selected_category': category_slug,
        'selected_date': date_filter,
        'selected_source': source_filter,
        'selected_sort': sort_filter,
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/search.html', context)


# ==============================================================================
# 5. DEDICATED TRENDING TOPICS VIEW
# ==============================================================================
def trending_topics_view(request):
    """
    Renders the dedicated Trending Topics page across Technology, Business, Politics, Sports, Science, Entertainment.
    """
    categories = Category.objects.all().order_by('order')
    trending_topics = TrendingTopic.objects.select_related('category').order_by('-velocity_percentage')
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]

    context = {
        'categories': categories,
        'trending_topics': trending_topics,
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/trending.html', context)


# ==============================================================================
# 6. AI NEWS SUMMARIZER VIEW
# ==============================================================================
def ai_summarizer_view(request):
    """
    Renders the AI News Summarizer page.
    """
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    context = {
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/summarizer.html', context)


# ==============================================================================
# 7. INTERACTIVE AI CHATBOT (TrendBot) VIEW
# ==============================================================================
def ask_ai_view(request):
    """
    Renders the TrendBot AI Chatbot interface.
    """
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    context = {
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/ask_ai.html', context)


# ==============================================================================
# 8. AUTHENTICATION VIEWS: LOGIN, REGISTER, LOGOUT, FORGOT PASSWORD
# ==============================================================================
@csrf_protect
def login_view(request):
    """
    Handles user login with error reporting and session setup.
    """
    if request.user.is_authenticated:
        return redirect('intelligence:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}. Intelligence terminal activated.")
            next_url = request.GET.get('next', 'intelligence:dashboard')
            return redirect(next_url)
        else:
            error = "Invalid analyst credentials. Please verify your username and password."

    breaking_news = NewsArticle.objects.filter(is_breaking=True)[:6]
    return render(request, 'auth/login.html', {'error': error, 'breaking_news': breaking_news})


@csrf_protect
def register_view(request):
    """
    Handles new user registration and profile creation.
    """
    if request.user.is_authenticated:
        return redirect('intelligence:dashboard')

    error = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            error = "All required fields must be provided."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."
        elif User.objects.filter(username=username).exists():
            error = "Username already allocated in the intelligence registry."
        elif User.objects.filter(email=email).exists():
            error = "Email address is already associated with an active terminal account."
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, f"Analyst profile successfully established for {username}.")
            return redirect('intelligence:dashboard')

    breaking_news = NewsArticle.objects.filter(is_breaking=True)[:6]
    return render(request, 'auth/register.html', {'error': error, 'breaking_news': breaking_news})


def logout_view(request):
    """
    Signs out user and redirects to homepage.
    """
    logout(request)
    messages.info(request, "Analyst session closed. Disconnected from command terminal.")
    return redirect('intelligence:index')


@csrf_protect
def forgot_password_view(request):
    """
    Password recovery interface with simulated secure token generation.
    """
    success = False
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        success = True

    breaking_news = NewsArticle.objects.filter(is_breaking=True)[:6]
    return render(request, 'auth/forgot_password.html', {'success': success, 'breaking_news': breaking_news})


# ==============================================================================
# 9. USER PROFILE & SAVED NEWS VIEWS
# ==============================================================================
def user_profile_view(request):
    """
    Renders and updates user profile, preferences, and reading history.
    """
    user = request.user
    if not user.is_authenticated:
        # Provide demo profile view for guest
        demo_user = User.objects.filter(username='demo_analyst').first()
        user = demo_user if demo_user else User.objects.first()

    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST' and request.user.is_authenticated:
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.save()

        profile.bio = request.POST.get('bio', profile.bio).strip()
        category_ids = request.POST.getlist('categories')
        if category_ids:
            profile.preferred_categories.set(Category.objects.filter(id__in=category_ids))
        profile.save()

        messages.success(request, "Analyst profile and topic preferences updated successfully.")
        return redirect('intelligence:profile')

    all_categories = Category.objects.all().order_by('order')
    saved_articles = profile.saved_articles.all().order_by('-published_at')
    if not saved_articles.exists():
        saved_articles = NewsArticle.objects.all()[:4]

    reading_history = profile.reading_history.all().order_by('-published_at')
    if not reading_history.exists():
        reading_history = NewsArticle.objects.all()[:5]

    breaking_news = NewsArticle.objects.filter(is_breaking=True)[:6]

    context = {
        'user': user,
        'profile': profile,
        'all_categories': all_categories,
        'saved_articles': saved_articles,
        'reading_history': reading_history,
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/profile.html', context)


def saved_news_view(request):
    """
    Renders dedicated Saved News & Bookmarks library.
    """
    user = request.user
    saved_articles = []
    if user.is_authenticated and hasattr(user, 'profile'):
        saved_articles = user.profile.saved_articles.all().order_by('-published_at')

    if not saved_articles:
        saved_articles = NewsArticle.objects.filter(impact_score__gte=94).order_by('-published_at')[:4]

    breaking_news = NewsArticle.objects.filter(is_breaking=True)[:6]
    context = {
        'saved_articles': saved_articles,
        'breaking_news': breaking_news,
    }
    return render(request, 'intelligence/saved_news.html', context)


# ==============================================================================
# BACKEND API ENDPOINTS
# ==============================================================================
@require_GET
def api_articles(request):
    """
    JSON API endpoint for searching, filtering, and sorting articles.
    """
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    topic_slug = request.GET.get('topic', '').strip()
    sentiment = request.GET.get('sentiment', '').strip()
    sort = request.GET.get('sort', 'latest').strip()

    articles = NewsArticle.objects.select_related('category', 'related_topic').all()

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(source_name__icontains=query) |
            Q(category__name__icontains=query)
        )

    if category_slug and category_slug != 'all':
        articles = articles.filter(category__slug=category_slug)

    if topic_slug:
        articles = articles.filter(related_topic__slug=topic_slug)

    if sentiment and sentiment != 'all':
        articles = articles.filter(sentiment__iexact=sentiment)

    if sort == 'impact':
        articles = articles.order_by('-impact_score', '-published_at')
    elif sort == 'velocity':
        articles = articles.order_by('-views_count', '-published_at')
    else:
        articles = articles.order_by('-published_at')

    return JsonResponse({
        'status': 'success',
        'count': articles.count(),
        'articles': [a.to_dict() for a in articles]
    })


@require_GET
def api_article_detail(request, slug):
    """
    Returns full details for a specific intelligence report.
    """
    article = get_object_or_404(NewsArticle.objects.select_related('category', 'related_topic'), slug=slug)
    article.views_count += 1
    article.save(update_fields=['views_count'])

    # Track in reading history if authenticated
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        request.user.profile.reading_history.add(article)

    return JsonResponse({
        'status': 'success',
        'article': article.to_dict()
    })


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api_bookmark_toggle(request, slug):
    """
    Toggles bookmark status on an article for the logged in user or returns status.
    """
    article = get_object_or_404(NewsArticle, slug=slug)
    is_bookmarked = False

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        if article in profile.saved_articles.all():
            profile.saved_articles.remove(article)
            is_bookmarked = False
        else:
            profile.saved_articles.add(article)
            is_bookmarked = True

    return JsonResponse({
        'status': 'success',
        'slug': slug,
        'bookmarked': is_bookmarked,
    })


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def api_summarize(request):
    """
    AI News Summarizer endpoint.
    Accepts text or url and summary format (short, detailed, keypoints).
    Returns synthesized text, word counts, and key metrics.
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            text = body.get('text', '').strip()
            url = body.get('url', '').strip()
            format_type = body.get('format', 'short').strip().lower()
        except Exception:
            text = request.POST.get('text', '').strip()
            url = request.POST.get('url', '').strip()
            format_type = request.POST.get('format', 'short').strip().lower()
    else:
        text = request.GET.get('text', '').strip()
        url = request.GET.get('url', '').strip()
        format_type = request.GET.get('format', 'short').strip().lower()

    if not text and not url:
        return JsonResponse({
            'status': 'error',
            'message': 'Please provide either dispatch text or a valid article URL.'
        }, status=400)

    # If URL provided but no text, synthesize from matching DB article or realistic mock
    if not text and url:
        matching = NewsArticle.objects.filter(Q(source_domain__icontains=url) | Q(slug__icontains=url.split('/')[-1])).first()
        if matching:
            text = matching.content
        else:
            text = f"Automated crawler extracted content from {url}. The report details significant technological breakthroughs and strategic macroeconomic shifts currently transforming global industrial supply chains."

    # Process summary formats
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if s.strip()]
    if not sentences:
        sentences = [text]

    word_count_in = len(text.split())

    if format_type == 'short':
        summary_text = " ".join(sentences[:2]) if len(sentences) >= 2 else sentences[0]
        summary_format_label = "Short Executive Briefing"
        bullet_points = []
    elif format_type == 'detailed':
        first_part = " ".join(sentences[:2])
        mid_part = " ".join(sentences[2:5]) if len(sentences) >= 5 else "Key structural factors reveal high-velocity adoption and cross-border regulatory harmonization."
        last_part = " ".join(sentences[5:8]) if len(sentences) >= 8 else "Long-term implications suggest significant cost reduction and operational resilience for commercial adopters through 2028."
        summary_text = f"<p><strong>Executive Overview:</strong> {first_part}</p><p><strong>Strategic Context:</strong> {mid_part}</p><p><strong>Future Outlook:</strong> {last_part}</p>"
        summary_format_label = "Detailed Intelligence Synthesis"
        bullet_points = []
    else: # keypoints
        summary_format_label = "Key Strategic Points"
        bullet_points = [
            sentences[0] if len(sentences) > 0 else "Demonstrated 100x efficiency gain over existing transformer accelerator architectures.",
            sentences[1] if len(sentences) > 1 else "Elimination of static power leakage through event-driven asynchronous clockless routing.",
            sentences[2] if len(sentences) > 2 else "Commercial tape-out pipelines targeting high-reliability edge aerospace deployments.",
            "Full regulatory compliance verified under international algorithmic safety protocols."
        ]
        summary_text = "<ul>" + "".join([f"<li>{bp}</li>" for bp in bullet_points]) + "</ul>"

    word_count_out = len(re.sub('<[^<]+?>', '', summary_text).split())
    saved_percentage = max(10, min(95, int((1 - (word_count_out / max(word_count_in, 1))) * 100)))

    return JsonResponse({
        'status': 'success',
        'format': format_type,
        'format_label': summary_format_label,
        'summary': summary_text,
        'bullets': bullet_points,
        'words_original': word_count_in,
        'words_summary': word_count_out,
        'saved_percentage': saved_percentage,
    })


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def api_chat(request):
    """
    TrendBot conversational AI endpoint.
    Answers inquiries about real-time news and trends based on TRENDORA articles database.
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            prompt = body.get('message', '').strip()
        except Exception:
            prompt = request.POST.get('message', '').strip()
    else:
        prompt = request.GET.get('message', '').strip()

    if not prompt:
        return JsonResponse({'status': 'error', 'message': 'Empty message received.'}, status=400)

    prompt_lower = prompt.lower()
    articles = NewsArticle.objects.all()
    trending = TrendingTopic.objects.all()

    # Contextual synthesis based on query
    matched_article = None
    for a in articles:
        if a.title.lower() in prompt_lower or any(word in prompt_lower for word in a.title.lower().split() if len(word) > 4):
            matched_article = a
            break

    if "trend" in prompt_lower or "technology" in prompt_lower or "today" in prompt_lower:
        top_trends = TrendingTopic.objects.order_by('-velocity_percentage')[:4]
        trend_bullets = "".join([f"<li><strong>{t.title}</strong>: +{t.velocity_percentage}% velocity across {t.volume_mentions:,} mentions ({t.category.name}).</li>" for t in top_trends])
        reply = f"""
<p>Here is the real-time velocity synthesis for today's highest-momentum trends:</p>
<ul style="margin: 0.6rem 0; padding-left: 1.2rem; line-height: 1.6;">
  {trend_bullets}
</ul>
<p>The standout breakout topic is <strong>{top_trends[0].title}</strong>, demonstrating an unprecedented acceleration curve driven by enterprise multi-agent workflows.</p>
"""
    elif "business" in prompt_lower or "market" in prompt_lower or "fund" in prompt_lower:
        biz_articles = NewsArticle.objects.filter(category__slug='business')[:2]
        bullets = "".join([f"<li><strong>{a.title}</strong> (Source: {a.source_name}): {a.summary}</li>" for a in biz_articles])
        reply = f"""
<p>Here is your executive briefing on today's leading business and capital flow signals:</p>
<ul style="margin: 0.6rem 0; padding-left: 1.2rem; line-height: 1.6;">
  {bullets}
</ul>
<p>Macro analysis indicates aggressive sovereign wealth allocation into nuclear-backed clean compute campuses across Middle Eastern and ASEAN consortia.</p>
"""
    elif "fusion" in prompt_lower or "tokamak" in prompt_lower:
        reply = """
<p><strong>Commercial Tokamak 22-Tesla Milestone:</strong></p>
<p>Engineers utilizing high-temperature rare-earth barium copper oxide (REBCO) magnet tapes have achieved a sustained 22-Tesla magnetic field for 72 continuous cryogenic hours.</p>
<p>Because magnetic plasma confinement pressure scales with the fourth power of magnetic field strength (B^4), a 22T field generates a <strong>16x amplification in plasma power density</strong> over classical 11T designs. This allows commercial fusion pilot reactors to shrink to the footprint of a standard warehouse.</p>
"""
    elif "treaty" in prompt_lower or "geneva" in prompt_lower or "politics" in prompt_lower or "policy" in prompt_lower:
        reply = """
<p><strong>Geneva Accord on Autonomous Systems:</strong></p>
<p>Delegates from 42 nations have ratified an algorithmic non-proliferation treaty. Key requirements include:</p>
<ul style="margin: 0.6rem 0; padding-left: 1.2rem; line-height: 1.6;">
  <li>Cryptographic provenance watermarking on models trained above 10^26 FLOPs.</li>
  <li>Strict prohibitions on autonomous offensive cyber-reconnaissance against civilian grid infrastructure.</li>
  <li>Spot-inspection oversight coordinated by the new International Algorithmic Safety Commission (IASC).</li>
</ul>
"""
    elif "neuromorphic" in prompt_lower or "chip" in prompt_lower:
        reply = """
<p><strong>3D Monolithic Neuromorphic Silicon:</strong></p>
<p>Lead researchers at Cambridge have verified a sub-2nm event-driven neuromorphic core achieving a <strong>100-fold reduction in energy draw</strong> (under 15 milliwatts).</p>
<p>By mimicking biological mammalian cortical sparse-coding with atomic-layer memristor crossbars directly bonded to logic, the processor operates strictly on asynchronous voltage spikes—consuming zero static leakage power during idle phases.</p>
"""
    elif matched_article:
        reply = f"""
<p>I found a verified intelligence report matching your inquiry:</p>
<div style="background: rgba(139, 92, 246, 0.1); border-left: 3px solid var(--purple-light); padding: 0.6rem 0.9rem; margin: 0.6rem 0; border-radius: 4px;">
  <strong>{matched_article.title}</strong><br>
  <span style="font-size: 0.8rem; color: var(--text-muted);">{matched_article.source_name} • Impact Score: {matched_article.impact_score}/100</span>
  <p style="margin-top: 0.4rem; font-size: 0.88rem;">{matched_article.summary}</p>
</div>
<p>Would you like me to synthesize the key strategic takeaways or compare this with related macro trends?</p>
"""
    else:
        recent = NewsArticle.objects.order_by('-published_at').first()
        reply = f"""
<p>I have scanned today's global intelligence feeds regarding <em>"{prompt}"</em>. While direct wire dispatches continue to stream in, our highest-velocity breaking story right now is:</p>
<p><strong>{recent.title}</strong> ({recent.source_name}, {recent.get_time_ago}).</p>
<p>{recent.summary}</p>
<p>Feel free to ask for a deeper summary, domain analysis, or key points on this dispatch!</p>
"""

    return JsonResponse({
        'status': 'success',
        'reply': reply,
        'timestamp': timezone.now().strftime('%H:%M:%S UTC'),
    })


@require_GET
def api_simulate_signal(request):
    """
    Simulates a new incoming real-time intelligence signal from global feeds.
    """
    simulated_signals = [
        {
            'title': 'Autonomous Micro-Drone Swarm Maps Subterranean Cavities via LIDAR Mesh',
            'category_slug': 'technology',
            'source_name': 'DARPA Telemetry Hub',
            'source_domain': 'darpa.mil',
            'summary': 'Coordinated agent swarms utilized peer-to-peer radio frequency ranging to navigate GPS-denied geological lava tubes in real-time.',
            'content': 'A demonstration conducted across underground test facilities validated decentralised spatial slam algorithms running on edge microcontrollers. The swarm achieved complete volumetric mapping without centralized synchronization nodes.',
            'takeaways': [
                'Peer-to-peer relative positioning removes GPS dependencies in extreme environments.',
                'Sub-centimeter spatial accuracy maintained across 4-kilometer tunnel complexes.',
                'Immediate applications for search-and-rescue and autonomous planetary exploration.'
            ],
            'read_time_minutes': 3,
            'impact_score': 91,
            'velocity_score': '+620% / 1h',
            'sentiment': 'BULLISH',
            'image_gradient': 'linear-gradient(135deg, #2e1065 0%, #3b0764 100%)',
            'hero_pattern': 'neural-grid',
            'is_breaking': True,
        },
        {
            'title': 'Multi-Principal High-Entropy Alloys Withstand 2,800°C Thermal Shock in Hypersonic Propulsion Trials',
            'category_slug': 'science',
            'source_name': 'AeroMatters Journal',
            'source_domain': 'aeromatters.org',
            'summary': 'Refractory alloys synthesized via laser powder bed fusion exhibit zero micro-fracturing under sustained Mach 7 boundary layer conditions.',
            'content': 'Advanced metallurgical formulations combining refractory metals have resolved one of aerospace engineerings toughest challenges: oxidation and catastrophic creep at ultra-high temperatures.',
            'takeaways': [
                'No structural phase decomposition up to 2,800 degrees Celsius.',
                '3D laser printing allows complex internal regenerative cooling channels.',
                'Commercial spacecraft re-entry heat shields set to adopt the new composition.'
            ],
            'read_time_minutes': 4,
            'impact_score': 94,
            'velocity_score': '+480% / 1h',
            'sentiment': 'HIGH IMPACT',
            'image_gradient': 'linear-gradient(135deg, #1e3a8a 0%, #0369a1 100%)',
            'hero_pattern': 'chip-mesh',
            'is_breaking': True,
        },
        {
            'title': 'Zero-Knowledge Machine Learning (ZK-ML) Circuit Proves 10M Parameters in Under 400ms',
            'category_slug': 'technology',
            'source_name': 'Cryptographic Review',
            'source_domain': 'iacr.org',
            'summary': 'Novel polynomial commitment schemes slash cryptographic proving overhead for proprietary neural network inference validation.',
            'content': 'Cryptographers have released benchmark proofs showing a 20-fold acceleration in ZK-SNARK generation for deep convolutional and attention layers. This enables trustless verification of AI model decisions without leaking model weights.',
            'takeaways': [
                'Prover latency reduced to 380ms for multi-layer vision architectures.',
                'Enables verifiably fair algorithmic decisions in legal, medical, and banking domains.',
                'Compatible with web-assembly execution environments directly inside browsers.'
            ],
            'read_time_minutes': 4,
            'impact_score': 89,
            'velocity_score': '+350% / 1h',
            'sentiment': 'BULLISH',
            'image_gradient': 'linear-gradient(135deg, #0e7490 0%, #155e75 100%)',
            'hero_pattern': 'quantum-lattice',
            'is_breaking': True,
        }
    ]

    selected = random.choice(simulated_signals)
    slug = f"signal-{int(timezone.now().timestamp())}"

    cat = Category.objects.filter(slug=selected['category_slug']).first()
    if not cat:
        cat = Category.objects.first()

    article = NewsArticle.objects.create(
        title=selected['title'],
        slug=slug,
        category=cat,
        source_name=selected['source_name'],
        source_domain=selected['source_domain'],
        source_badge_color=cat.color_code,
        published_at=timezone.now(),
        summary=selected['summary'],
        content=selected['content'],
        key_takeaways_json=json.dumps(selected['takeaways']),
        read_time_minutes=selected['read_time_minutes'],
        impact_score=selected['impact_score'],
        velocity_score=selected['velocity_score'],
        sentiment=selected['sentiment'],
        image_gradient=selected['image_gradient'],
        hero_pattern=selected['hero_pattern'],
        is_breaking=selected['is_breaking'],
        views_count=random.randint(150, 450),
        bookmarks_count=random.randint(12, 50)
    )

    return JsonResponse({
        'status': 'success',
        'signal': article.to_dict()
    })
