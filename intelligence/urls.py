from django.urls import path
from . import views

app_name = 'intelligence'

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.advanced_search, name='advanced_search'),
    path('trending/', views.trending_topics_view, name='trending'),
    path('summarizer/', views.ai_summarizer_view, name='ai_summarizer'),
    path('ask-ai/', views.ask_ai_view, name='ask_ai'),
    path('profile/', views.user_profile_view, name='profile'),
    path('saved/', views.saved_news_view, name='saved_news'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),

    # API Endpoints
    path('api/articles/', views.api_articles, name='api_articles'),
    path('api/articles/<slug:slug>/', views.api_article_detail, name='api_article_detail'),
    path('api/bookmark/<slug:slug>/', views.api_bookmark_toggle, name='api_bookmark_toggle'),
    path('api/summarize/', views.api_summarize, name='api_summarize'),
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/simulate-signal/', views.api_simulate_signal, name='api_simulate_signal'),
]
