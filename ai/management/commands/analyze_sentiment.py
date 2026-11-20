from django.core.management.base import BaseCommand
from news.models import NewsArticle
from ai.services.sentiment_service import SentimentAnalysisService

class Command(BaseCommand):
    help = 'Runs sentiment classification across collected news articles in the database.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=20, help='Maximum articles to evaluate')

    def handle(self, *args, **options):
        limit = options.get('limit')
        self.stdout.write(self.style.NOTICE(f"Initiating sentiment analysis on up to {limit} articles..."))

        service = SentimentAnalysisService()
        articles = NewsArticle.objects.all().order_by('-published_at')[:limit]

        updated = 0
        for a in articles:
            res = service.analyze_and_update_article(a.id)
            self.stdout.write(f"[{res['sentiment']}] ({res['confidence'] * 100:.0f}%) {a.title[:65]}...")
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Sentiment analysis completed for {updated} articles."))
