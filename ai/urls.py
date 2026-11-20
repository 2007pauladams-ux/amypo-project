from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Template Page Views
    path('summarizer/', views.summarizer_view, name='ai_summarizer'),
    path('ask-ai/', views.ask_ai_view, name='ask_ai'),

    # REST / AJAX API Endpoints
    path('api/summarize/', views.api_summarize, name='api_summarize'),
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/rag/', views.api_rag_query, name='api_rag_query'),
    path('api/sentiment/', views.api_sentiment, name='api_sentiment'),
    path('api/trends/intelligence/', views.api_trend_intelligence, name='api_trend_intelligence'),
    path('api/faiss/reindex/', views.api_faiss_reindex, name='api_faiss_reindex'),
]
