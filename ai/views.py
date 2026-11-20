import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .services.groq_service import GroqService
from .services.summarizer_service import AiSummarizerService
from .services.trendbot_service import TrendBotService
from .services.rag_service import RagPipeline
from .services.sentiment_service import SentimentAnalysisService
from .services.trend_intelligence_service import TrendIntelligenceService
from .services.vector_store import FaissVectorStore

from news.models import NewsArticle
from trends.models import TrendingTopic

def summarizer_view(request):
    """
    AI News Summarizer page for TRENDORA.
    Accepts article URL or text, generates Short, Detailed, or Key Points summaries via Groq LLM.
    """
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    sample_articles = NewsArticle.objects.all().order_by('-impact_score')[:4]

    context = {
        'breaking_news': breaking_news,
        'sample_articles': sample_articles,
    }
    return render(request, 'intelligence/summarizer.html', context)


def ask_ai_view(request):
    """
    Interactive TrendBot AI Chatbot interface.
    Powered by the RAG pipeline and Groq LLM.
    """
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    trending_topics = TrendingTopic.objects.all().order_by('-calculated_score')[:5]

    suggested_questions = [
        "What are today's top technology trends?",
        "Summarize recent semiconductor breakthroughs",
        "What is happening in quantum computing?",
        "Show breaking dispatches",
        "Explain sovereign digital reserves",
    ]

    context = {
        'breaking_news': breaking_news,
        'trending_topics': trending_topics,
        'suggested_questions': suggested_questions,
    }
    return render(request, 'intelligence/ask_ai.html', context)


@csrf_exempt
@require_POST
def api_summarize(request):
    """
    JSON API endpoint for AI news summarization using Groq LLM.
    POST /api/summarize/
    Payload: {"text": "...", "url": "...", "format": "short"|"detailed"|"keypoints"}
    """
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    else:
        data = request.POST

    text = data.get('text', '').strip()
    url = data.get('url', '').strip()
    format_type = data.get('format', 'short').strip().lower()

    if format_type not in ('short', 'detailed', 'keypoints'):
        format_type = 'short'

    if not text and not url:
        return JsonResponse({
            'status': 'error',
            'message': 'Please provide article text or a valid URL to summarize.'
        }, status=400)

    service = AiSummarizerService()
    result = service.summarize(text=text, url=url, format_type=format_type)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def api_chat(request):
    """
    JSON API endpoint for TrendBot RAG chatbot interaction.
    POST /api/chat/
    Payload: {"message": "...", "history": [...]}
    """
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    else:
        data = request.POST

    message = data.get('message', '').strip()
    history = data.get('history', [])

    service = TrendBotService()
    result = service.process_message(
        user_message=message,
        user=request.user if request.user.is_authenticated else None,
        conversation_history=history
    )

    return JsonResponse({
        'status': 'success',
        'reply': result.get('reply', ''),
        'message': result.get('reply', ''),
        'raw_reply': result.get('raw_reply', ''),
        'citations': result.get('citations', []),
        'suggestions': result.get('suggestions', []),
        'context_count': result.get('context_count', 0),
    })


@csrf_exempt
@require_POST
def api_rag_query(request):
    """
    Direct RAG semantic search and answer endpoint.
    POST /api/rag/
    Payload: {"query": "...", "top_k": 4}
    """
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    else:
        data = request.POST

    query = data.get('query', '').strip()
    top_k = min(int(data.get('top_k', 4)), 10)

    if not query:
        return JsonResponse({'status': 'error', 'message': 'Query cannot be empty.'}, status=400)

    pipeline = RagPipeline()
    result = pipeline.run_rag(query=query, top_k=top_k)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def api_sentiment(request):
    """
    Sentiment analysis endpoint.
    POST /api/sentiment/
    Payload: {"article_id": 1} OR {"title": "...", "text": "..."}
    """
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    else:
        data = request.POST

    service = SentimentAnalysisService()

    article_id = data.get('article_id')
    if article_id:
        result = service.analyze_and_update_article(article_id)
        return JsonResponse(result)

    title = data.get('title', '').strip()
    text = data.get('text', '').strip()
    if not title and not text:
        return JsonResponse({'status': 'error', 'message': 'Either article_id or title/text is required.'}, status=400)

    result = service.analyze_text(title, text)
    return JsonResponse(result)


@require_GET
def api_trend_intelligence(request):
    """
    AI-assisted trend intelligence endpoint.
    GET /api/trends/intelligence/?topic=<topic_id_or_slug>
    """
    topic_query = request.GET.get('topic', '').strip()
    service = TrendIntelligenceService()

    if topic_query:
        result = service.analyze_trending_topic(topic_query)
        return JsonResponse(result)

    all_results = service.analyze_all_trends()
    return JsonResponse({'status': 'success', 'trends_intelligence': all_results})


@csrf_exempt
@require_POST
def api_faiss_reindex(request):
    """
    Triggers re-indexing of all database news articles into FAISS vector store.
    POST /api/faiss/reindex/
    """
    store = FaissVectorStore()
    count = store.rebuild_index_from_db()
    return JsonResponse({
        'status': 'success',
        'message': f'FAISS index rebuilt with {count} documents.',
        'total_indexed': store.count()
    })
