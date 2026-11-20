from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from news.models import NewsCategory, NewsArticle
from trends.models import TrendingTopic
from trends.services.trend_detector import TrendDetectionEngine

class TrendsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = NewsCategory.objects.create(
            name='Artificial Intelligence',
            slug='artificial-intelligence',
            icon='cpu',
            badge_class='badge-purple'
        )
        self.topic = TrendingTopic.objects.create(
            title='Autonomous AI Agents',
            slug='autonomous-ai-agents',
            category=self.category,
            volume_mentions=45000,
            velocity_percentage=280,
            sentiment='bullish',
            trend_direction='hot',
            movement_text='+15 ranks today',
            article_count=12,
            is_hot=True,
            calculated_score=94.5
        )
        # Create article for trend detector test
        self.article = NewsArticle.objects.create(
            title='Autonomous AI Agents Breakthrough in Enterprise Computing',
            slug='autonomous-ai-agents-breakthrough-enterprise',
            category=self.category,
            url='https://intel.trendora.io/dispatches/autonomous-ai-agents-breakthrough',
            summary='Autonomous AI agents revolutionize asynchronous workflows with zero human intervention.',
            content='Comprehensive report detailing autonomous multi-agent systems and real-time execution.',
            impact_score=92,
            published_at=timezone.now()
        )

    def test_trending_topic_model_methods(self):
        """Test sparkline points generator and dict conversion."""
        points = self.topic.get_sparkline_points()
        self.assertIsInstance(points, list)
        data = self.topic.to_dict()
        self.assertEqual(data['title'], 'Autonomous AI Agents')
        self.assertEqual(data['velocity_percentage'], 280)
        self.assertEqual(data['calculated_score'], 94.5)

    def test_trend_detection_engine(self):
        """Test the algorithmic trend detector parses articles and stores calculated scores."""
        engine = TrendDetectionEngine(days_lookback=7, min_article_count=1)
        result = engine.run_detection()
        self.assertGreaterEqual(result['articles_scanned'], 1)
        self.assertGreaterEqual(result['topics_persisted'], 1)
        
        # Verify an updated or created trend exists with positive calculated_score
        top_trend = TrendingTopic.objects.order_by('-calculated_score').first()
        self.assertIsNotNone(top_trend)
        self.assertGreater(top_trend.calculated_score, 0)

    def test_trending_topics_view(self):
        """Test trending topics page renders with hot trends."""
        response = self.client.get(reverse('trends:trending'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trending Topics')
        self.assertContains(response, 'Autonomous AI Agents')

    def test_api_trends_endpoint(self):
        """Test /api/trends/ JSON endpoint."""
        response = self.client.get(reverse('trends:api_trends'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(data['count'], 1)
        self.assertEqual(data['trends'][0]['slug'], self.topic.slug)
