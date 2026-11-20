from django.core.management.base import BaseCommand
from trends.services.trend_detector import TrendDetectionEngine

class Command(BaseCommand):
    help = 'Executes the TRENDORA Trend Detection Algorithm across collected news articles.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of previous days of news articles to analyze'
        )
        parser.add_argument(
            '--min-count',
            type=int,
            default=1,
            help='Minimum number of article mentions required to qualify as trend'
        )

    def handle(self, *args, **options):
        days = options.get('days')
        min_count = options.get('min_count')
        self.stdout.write(self.style.NOTICE(f"Initiating algorithmic trend analysis (lookback={days} days, min_count={min_count})..."))

        engine = TrendDetectionEngine(days_lookback=days, min_article_count=min_count)
        result = engine.run_detection()

        self.stdout.write(self.style.SUCCESS(
            f"Trend detection complete: scanned {result['articles_scanned']} articles, "
            f"extracted {result['unique_topics_extracted']} candidates, "
            f"persisted {result['topics_persisted']} ranked trending topics."
        ))
