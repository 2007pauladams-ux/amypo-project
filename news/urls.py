from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('search/', views.advanced_search_view, name='advanced_search'),
    path('saved/', views.saved_news_view, name='saved_news'),

    # REST / AJAX APIs
    path('api/articles/', views.api_articles, name='api_articles'),
    path('api/articles/<slug:slug>/', views.api_article_detail, name='api_article_detail'),
    path('api/bookmark/<slug:slug>/', views.api_bookmark_toggle, name='api_bookmark_toggle'),
    path('api/user-bookmarks/', views.api_user_bookmarks, name='api_user_bookmarks'),
    path('api/simulate-signal/', views.api_simulate_signal, name='api_simulate_signal'),
]
