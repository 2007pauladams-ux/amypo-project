import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError

from news.models import NewsCategory, NewsSource, NewsArticle, SavedArticle, SearchHistory
from news.services.newsapi_service import NewsAPIService

class NewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = NewsCategory.objects.create(
            name='Quantum Computing',
            slug='quantum-computing',
            icon='cpu',
            badge_class='badge-purple'
        )
        self.source = NewsSource.objects.create(
            name='Frontier Wire',
            slug='frontier-wire',
            domain='frontier.intel'
        )
        self.article = NewsArticle.objects.create(
            title='Superconducting Qubit Array Demonstrates Quantum Supremacy',
            slug='superconducting-qubit-array-quantum-supremacy',
            category=self.category,
            source=self.source,
            source_name='Frontier Wire',
            source_domain='frontier.intel',
            url='https://intel.trendora.io/dispatches/superconducting-qubit-array',
            summary='Researchers demonstrate fault-tolerant logical qubit operations.',
            content='Full briefing report on superconducting qubit scaling and cryogenic isolation.',
            key_takeaways_json=json.dumps(['Logical error rates drop by 80%', 'Cryogenic controller operates at 4K']),
            impact_score=95,
            is_featured=True,
            is_breaking=True
        )
        self.user = User.objects.create_user(
            username='cadet_analyst',
            email='cadet@test.intel',
            password='TestPassword123!'
        )

    def test_article_url_unique_constraint(self):
        """Test that duplicate canonical article URLs are prevented by database constraint."""
        with self.assertRaises(IntegrityError):
            NewsArticle.objects.create(
                title='Duplicate Attempt',
                slug='duplicate-attempt',
                category=self.category,
                url='https://intel.trendora.io/dispatches/superconducting-qubit-array',
                summary='Duplicate summary.',
                content='Duplicate content.'
            )

    def test_newsapi_service_deduplication(self):
        """Test that NewsAPIService persists raw items and avoids duplicating canonical URLs."""
        service = NewsAPIService()
        mock_raw = [
            {
                'title': 'Autonomous AI Agents Surge in Production',
                'description': 'AI agents deploy to high-frequency finance.',
                'content': 'Full article text regarding autonomous AI agent systems in production.',
                'url': 'https://intel.trendora.io/dispatches/ai-agents-surge-test',
                'publishedAt': timezone.now().isoformat(),
                'source': {'name': 'Frontier Wire'},
            }
        ]
        # First insertion
        saved, created, errors = service.process_and_save_articles(mock_raw, default_category_slug='technology')
        self.assertEqual(created, 1)
        self.assertEqual(saved, 1)

        # Second insertion with same URL
        saved2, created2, errors2 = service.process_and_save_articles(mock_raw, default_category_slug='technology')
        self.assertEqual(created2, 0)
        self.assertEqual(saved2, 1)

    def test_index_view_renders_successfully(self):
        """Test homepage renders successfully with dynamic database articles."""
        response = self.client.get(reverse('news:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TRENDORA')
        self.assertContains(response, self.article.title)

    def test_dashboard_view_renders_successfully(self):
        """Test user dashboard renders with statistics and feeds."""
        response = self.client.get(reverse('news:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Command Dashboard')
        self.assertContains(response, self.article.title)

    def test_advanced_search_view_and_filtering(self):
        """Test advanced search view with keyword query and category filter."""
        response = self.client.get(reverse('news:advanced_search'), {
            'q': 'Superconducting',
            'category': 'quantum-computing',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertTrue(SearchHistory.objects.filter(query='Superconducting').exists())

    def test_api_articles_endpoint(self):
        """Test /api/articles/ JSON endpoint."""
        response = self.client.get(reverse('news:api_articles'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(data['count'], 1)

    def test_api_article_detail_endpoint(self):
        """Test /api/articles/<slug>/ detail endpoint."""
        response = self.client.get(reverse('news:api_article_detail', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['article']['title'], self.article.title)

    def test_api_bookmark_toggle(self):
        """Test bookmark toggle adds and removes SavedArticle."""
        self.client.login(username='cadet_analyst', password='TestPassword123!')
        
        # Toggle ON
        res1 = self.client.post(reverse('news:api_bookmark_toggle', kwargs={'slug': self.article.slug}))
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json()['is_saved'])
        self.assertTrue(SavedArticle.objects.filter(user=self.user, article=self.article).exists())

        # Toggle OFF
        res2 = self.client.post(reverse('news:api_bookmark_toggle', kwargs={'slug': self.article.slug}))
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()['is_saved'])
        self.assertFalse(SavedArticle.objects.filter(user=self.user, article=self.article).exists())

    def test_api_simulate_signal(self):
        """Test /api/simulate-signal/ endpoint returns a valid intelligence signal."""
        response = self.client.get(reverse('news:api_simulate_signal'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('title', data['signal'])
