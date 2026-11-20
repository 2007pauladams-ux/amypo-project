from django.urls import path
from . import views

app_name = 'trends'

urlpatterns = [
    path('trending/', views.trending_topics_view, name='trending'),
    path('api/trends/', views.api_trending_topics, name='api_trends'),
]
