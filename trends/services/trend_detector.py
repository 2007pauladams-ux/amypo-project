import re
import math
import logging
from collections import defaultdict, Counter
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify

from news.models import NewsArticle, NewsCategory
from trends.models import TrendingTopic

logger = logging.getLogger('trendora.trends')

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'up', 'about', 'into', 'over', 'after', 'beneath', 'under', 'above',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
    'does', 'did', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'this',
    'that', 'these', 'those', 'it', 'its', 'he', 'she', 'they', 'them', 'their',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just',
    'new', 'now', 'says', 'said', 'first', 'day', 'days', 'week', 'year', 'years',
    'via', 'per', 'across', 'unveils', 'record', 'enters', 'production', 'achieve',
    'achieves', 'demonstrate', 'demonstrates', 'breakthrough', 'announces', 'signs'
}

ENTITY_SEED_PATTERNS = [
    r'autonomous\s+ai\s+agents?',
    r'multi-agent\s+networks?',
    r'high-na\s+euv\s+lithography',
    r'semiconductor\s+fabs?',
    r'commercial\s+fusion',
    r'tokamak\s+fusion',
    r'quantum\s+error\s+correction',
    r'quantum\s+computing',
    r'sovereign\s+digital\s+reserves?',
    r'central\s+bank\s+settlement',
    r'solid-state\s+batter(?:y|ies)',
    r'neural\s+bci',
    r'brain-computer\s+interface',
    r'orbital\s+space\s+freight',
    r'space\s+constellation',
    r'generative\s+cinema',
    r'volumetric\s+splatting',
    r'biometric\s+telemetry',
    r'deep-sea\s+mineral',
]

class TrendDetectionEngine:
    """
    TRENDORA Trending Topic Detection Engine.
    Analyzes article titles, keyphrases, and summaries.
    Computes frequency and publication recency decay scores:
      Score = Sum( (Impact / 100) * (1 / (1 + (hours_elapsed * 0.15))) ) * Frequency_Multiplier
    Distinguishes algorithmic internal calculation from broadcast mention volume.
    """

    def __init__(self, days_lookback=7, min_article_count=1):
        self.days_lookback = days_lookback
        self.min_article_count = min_article_count

    def run_detection(self):
        """
        Executes the detection pipeline. Returns a dict of summary metrics.
        """
        now = timezone.now()
        since = now - timedelta(days=self.days_lookback)
        articles = list(NewsArticle.objects.filter(published_at__gte=since).select_related('category'))

        if not articles:
            articles = list(NewsArticle.objects.all().select_related('category')[:40])

        logger.info(f"Analyzing {len(articles)} articles for trend synthesis...")

        # 1. Extract candidate topics and map to articles
        topic_article_map = defaultdict(list)
        topic_category_counts = defaultdict(Counter)

        for article in articles:
            text = f"{article.title} {article.summary}"
            extracted_phrases = self._extract_keyphrases(text)

            for phrase in extracted_phrases:
                topic_article_map[phrase].append(article)
                if article.category:
                    topic_category_counts[phrase][article.category] += 1

        # 2. Score topics based on frequency, recency, and impact score
        scored_topics = []
        for phrase, arts in topic_article_map.items():
            if len(arts) < self.min_article_count:
                continue

            recency_score = 0.0
            total_impact = 0
            for art in arts:
                hours_ago = max(0.1, (now - art.published_at).total_seconds() / 3600.0)
                # Exponential/harmonic recency decay
                time_weight = 1.0 / (1.0 + (hours_ago * 0.12))
                recency_score += (art.impact_score / 100.0) * time_weight
                total_impact += art.impact_score

            # Frequency multiplier (logarithmic scaling to prevent runaway spikes)
            freq_mult = 1.0 + math.log(1.0 + len(arts))
            calculated_score = round(recency_score * freq_mult * 10.0, 2)

            # Dominant category
            category = None
            if topic_category_counts[phrase]:
                category = topic_category_counts[phrase].most_common(1)[0][0]
            if not category:
                category = NewsCategory.objects.first()

            scored_topics.append({
                'title': phrase.title(),
                'articles': arts,
                'count': len(arts),
                'calculated_score': calculated_score,
                'category': category,
                'avg_impact': total_impact / len(arts),
            })

        # 3. Sort by calculated algorithmic score
        scored_topics.sort(key=lambda x: x['calculated_score'], reverse=True)

        # 4. Synchronize to database
        saved_topics = []
        for rank, item in enumerate(scored_topics[:20]):
            title = item['title'][:140]
            slug = slugify(title)[:150] or f"trend-{rank}"
            cat = item['category']
            count = item['count']
            score = item['calculated_score']

            # Calculate simulated external volume vs internal algorithmic score
            base_vol = int(score * 420) + (count * 1500)
            velocity = int(min(450, max(45, (score * 3.8) + (rank * -5))))

            if rank < 3 or velocity > 180:
                direction = 'hot'
                is_hot = True
                movement = f"+{20 - rank} ranks today"
                sentiment = 'bullish'
            elif velocity > 120:
                direction = 'up'
                is_hot = rank < 6
                movement = f"+{12 - rank} this week"
                sentiment = 'critical' if rank % 2 == 0 else 'bullish'
            else:
                direction = 'steady'
                is_hot = False
                movement = f"Rank #{rank+1} stable"
                sentiment = 'neutral'

            # Generate realistic sparkline progression
            p1 = max(15, min(95, int(score * 0.4)))
            p2 = max(15, min(95, int(p1 + (velocity * 0.1))))
            p3 = max(15, min(95, int(p2 - 5)))
            p4 = max(20, min(95, int(p3 + 12)))
            p5 = max(30, min(98, int(p4 + 8)))
            p6 = max(40, min(99, int(p5 + 6)))
            p7 = max(50, min(100, int(score)))
            sparkline = f"{p1},{p2},{p3},{p4},{p5},{p6},{p7}"

            summary = f"Identified across {count} verified dispatch{'es' if count > 1 else ''}. Real-time momentum calculated at {velocity}% acceleration."

            topic, created = TrendingTopic.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'category': cat,
                    'volume_mentions': base_vol,
                    'velocity_percentage': velocity,
                    'sentiment': sentiment,
                    'trend_direction': direction,
                    'movement_text': movement,
                    'article_count': count,
                    'is_hot': is_hot,
                    'sparkline_data': sparkline,
                    'summary': summary,
                    'calculated_score': score,
                }
            )

            # Link articles to this trend
            for a in item['articles']:
                if not a.related_topic:
                    a.related_topic = topic
                    a.save(update_fields=['related_topic'])

            saved_topics.append(topic)

        logger.info(f"Trending topic detection synthesized {len(saved_topics)} top trends.")
        return {
            'articles_scanned': len(articles),
            'unique_topics_extracted': len(scored_topics),
            'topics_persisted': len(saved_topics),
        }

    def _extract_keyphrases(self, text):
        """
        Extracts multi-word entity phrases and key unigrams.
        """
        cleaned = text.lower()
        phrases = set()

        # Check pre-seeded known entity patterns
        for pattern in ENTITY_SEED_PATTERNS:
            matches = re.findall(pattern, cleaned)
            for m in matches:
                phrases.add(m.strip())

        # Extract 2-gram and 3-gram noun phrases
        words = re.findall(r'[a-z0-9\-]+', cleaned)
        filtered_words = [w for w in words if len(w) > 2 and w not in STOPWORDS]

        for i in range(len(filtered_words) - 1):
            two_gram = f"{filtered_words[i]} {filtered_words[i+1]}"
            if len(two_gram) > 6:
                phrases.add(two_gram)

        for i in range(len(filtered_words) - 2):
            three_gram = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
            if len(three_gram) > 10:
                phrases.add(three_gram)

        return phrases
