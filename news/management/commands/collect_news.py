import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.services.newsapi_service import NewsAPIService

logger = logging.getLogger('trendora.collect_news')

class Command(BaseCommand):
    help = 'Fetches real-time news articles from NewsAPI, normalizes payloads, and persists them without duplicates.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='News category filter (technology, business, science, sports, entertainment, general)'
        )
        parser.add_argument(
            '--query',
            type=str,
            default=None,
            help='Search keyword or topic query'
        )
        parser.add_argument(
            '--country',
            type=str,
            default=None,
            help='ISO 2-letter country code (e.g. us, gb)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of articles to retrieve per batch'
        )
        parser.add_argument(
            '--everything',
            action='store_true',
            help='Query NewsAPI /everything endpoint instead of /top-headlines'
        )

    def handle(self, *args, **options):
        start_time = time.time()
        category = options.get('category')
        query = options.get('query')
        country = options.get('country')
        limit = options.get('limit')
        use_everything = options.get('everything')

        timestamp_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        self.stdout.write(self.style.SUCCESS(f"[{timestamp_str}] Initiating TRENDORA Autonomous News Collection Pipeline..."))

        service = NewsAPIService()
        configured = service.is_configured()
        if configured:
            self.stdout.write(self.style.NOTICE("NewsAPI client authenticated via environment key."))
        else:
            self.stdout.write(self.style.WARNING("NewsAPI key missing or placeholder. Running synthetic signal engine."))

        raw_articles = []
        try:
            if use_everything or (query and not category):
                self.stdout.write(f"Executing deep query search for: '{query or 'technology'}' (limit={limit})...")
                raw_articles = service.fetch_everything(query=query, page_size=limit)
            else:
                self.stdout.write(f"Querying top headlines (category={category or 'all'}, country={country or 'default'}, limit={limit})...")
                raw_articles = service.fetch_top_headlines(category=category, query=query, country=country, page_size=limit)

            self.stdout.write(f"Retrieved {len(raw_articles)} raw intelligence items. Beginning normalization & deduplication...")
            
            saved_count, created_count, error_count = service.process_and_save_articles(
                raw_articles,
                default_category_slug=category or 'technology'
            )

            duration = round(time.time() - start_time, 2)
            self.stdout.write(self.style.SUCCESS(
                f"Collection complete in {duration}s: {saved_count} processed, {created_count} new dispatches added, {error_count} errors."
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"News collection pipeline encountered an error: {e}"))
            logger.error(f"News collection failed: {e}", exc_info=True)
