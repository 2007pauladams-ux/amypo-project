from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from news import views as news_views
from trends import views as trends_views
from ai import views as ai_views
from accounts import views as accounts_views

intelligence_patterns = ([
    path('', news_views.index_view, name='index'),
    path('dashboard/', news_views.dashboard_view, name='dashboard'),
    path('trending/', trends_views.trending_topics_view, name='trending'),
    path('search/', news_views.advanced_search_view, name='advanced_search'),
    path('summarizer/', ai_views.summarizer_view, name='ai_summarizer'),
    path('ask-ai/', ai_views.ask_ai_view, name='ask_ai'),
    path('saved/', news_views.saved_news_view, name='saved_news'),
    path('profile/', accounts_views.profile_view, name='profile'),
    path('login/', accounts_views.login_view, name='login'),
    path('register/', accounts_views.register_view, name='register'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('forgot-password/', accounts_views.forgot_password_view, name='forgot_password'),
], 'intelligence')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Modular Applications
    path('', include('news.urls')),
    path('', include('accounts.urls')),
    path('', include('trends.urls')),
    path('', include('ai.urls')),

    # Backward-compatible template namespace
    path('', include(intelligence_patterns, namespace='intelligence')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
