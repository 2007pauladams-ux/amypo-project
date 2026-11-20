import json
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .services.summarizer_service import AiSummarizerService
from .services.trendbot_service import TrendBotService
from news.models import NewsArticle
from trends.models import TrendingTopic

def summarizer_view(request):
    """
    AI News Summarizer page for TRENDORA.
    Supports article URL input, text input area, and formats (Short, Detailed, Key Points).
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
    Interactive TrendBot Chatbot interface.
    """
    breaking_news = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:6]
    trending_topics = TrendingTopic.objects.all().order_by('-calculated_score')[:5]

    suggested_questions = [
        "What are today's top technology trends?",
        "Summarize the latest business news.",
        "What is happening in quantum computing?",
        "Show breaking dispatches",
        "Explain high-NA EUV lithography",
    ]

    context = {
        'breaking_news': breaking_news,
        'trending_topics': trending_topics,
        'suggested_questions': suggested_questions,
    }
    return render(request, 'intelligence/ask_ai.html', context)


@require_POST
def api_summarize(request):
    """
    JSON API endpoint for AI news summarization.
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

    raw_summary = result.get('summary', '')
    # Convert simple markdown to html for innerHTML rendering
    html_summary = raw_summary.replace('\n\n', '<br><br>').replace('\n', '<br>')
    html_summary = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_summary)
    html_summary = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_summary)
    html_summary = re.sub(r'### (.*?)<br>', r'<h3 style="color:var(--purple-light); margin:0.8rem 0 0.4rem;">\1</h3>', html_summary)
    html_summary = re.sub(r'#### (.*?)<br>', r'<h4 style="color:var(--text-primary); margin:0.6rem 0 0.3rem;">\1</h4>', html_summary)

    format_labels = {
        'short': 'Short Executive Summary',
        'detailed': 'Detailed Strategic Briefing',
        'keypoints': 'Actionable Key Points'
    }

    words_orig = result.get('original_word_count', 0)
    words_summ = result.get('summary_word_count', 0)
    saved_pct = max(10, min(85, int((1 - (words_summ / max(words_orig, 1))) * 100)))

    return JsonResponse({
        'status': 'success',
        'format': format_type,
        'format_label': format_labels.get(format_type, 'Summary Briefing'),
        'saved_percentage': saved_pct,
        'words_original': words_orig,
        'words_summary': words_summ,
        'summary': html_summary,
        'raw_summary': raw_summary,
        'title': result.get('title', ''),
        'source': result.get('source', ''),
        'estimated_read_time': result.get('estimated_read_time', '1 min read'),
    })


@require_POST
def api_chat(request):
    """
    JSON API endpoint for TrendBot conversational interaction.
    POST /api/chat/
    Payload: {"message": "..."}
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
    service = TrendBotService()
    result = service.process_message(user_message=message, user=request.user)

    raw_reply = result.get('response', '')
    # Convert markdown to html for bubble-text
    html_reply = raw_reply.replace('\n\n', '<br><br>').replace('\n', '<br>')
    html_reply = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_reply)
    html_reply = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_reply)

    return JsonResponse({
        'status': 'success',
        'reply': html_reply,
        'message': html_reply,
        'raw_message': raw_reply,
        'suggestions': result.get('suggestions', []),
    })
