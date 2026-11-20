from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('summarizer/', views.summarizer_view, name='ai_summarizer'),
    path('ask-ai/', views.ask_ai_view, name='ask_ai'),

    # REST / AJAX APIs
    path('api/summarize/', views.api_summarize, name='api_summarize'),
    path('api/chat/', views.api_chat, name='api_chat'),
]
