from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from intelligence.models import Category, TrendingTopic, NewsArticle, UserProfile
import json

class TrendoraComprehensiveTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Technology',
            slug='technology',
            icon='cpu',
            color_code='#8b5cf6',
            badge_class='badge-purple'
        )
        self.topic = TrendingTopic.objects.create(
            title='Autonomous Agent Swarms',
            slug='autonomous-agent-swarms',
            category=self.category,
            volume_mentions=150000,
            velocity_percentage=380,
            sentiment='bullish',
            trend_direction='hot',
            movement_text='▲ Surging Hot (+380%)',
            article_count=35,
            is_hot=True,
            sparkline_data='20,40,60,80,95'
        )
        self.article = NewsArticle.objects.create(
            title='Neuromorphic Chip Milestone Achieved',
            slug='neuromorphic-chip-milestone',
            category=self.category,
            source_name='MIT Tech Review',
            source_domain='technologyreview.com',
            published_at=timezone.now(),
            summary='Testing summary of neuromorphic computing breakthrough.',
            content='Full testing content of intelligence report explaining event-driven spikes.',
            key_takeaways_json=json.dumps(['100x reduction in power envelope', 'Zero static leakage']),
            read_time_minutes=4,
            impact_score=95,
            velocity_score='+420% / 1h',
            sentiment='BULLISH',
            related_topic=self.topic,
            is_featured=True,
            is_breaking=True
        )
        self.user = User.objects.create_user(
            username='test_analyst',
            email='analyst@test.io',
            password='Password123!',
            first_name='Alex',
            last_name='Rivers'
        )

    def test_homepage(self):
        res = self.client.get(reverse('intelligence:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'TRENDORA')
        self.assertContains(res, 'Neuromorphic Chip Milestone Achieved')

    def test_dashboard(self):
        res = self.client.get(reverse('intelligence:dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Intelligence Command Dashboard')
        self.assertContains(res, 'TOTAL MONITORED DISPATCHES')
        self.assertContains(res, 'Trending Velocity Radar')

    def test_advanced_search(self):
        res = self.client.get(reverse('intelligence:advanced_search'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Advanced News & Trend Search')

        # With query
        res_q = self.client.get(reverse('intelligence:advanced_search') + '?q=neuromorphic')
        self.assertEqual(res_q.status_code, 200)
        self.assertContains(res_q, 'Neuromorphic Chip Milestone Achieved')

    def test_trending_topics_page(self):
        res = self.client.get(reverse('intelligence:trending'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Global Trending Macro Topics')
        self.assertContains(res, 'Autonomous Agent Swarms')

    def test_ai_summarizer_page(self):
        res = self.client.get(reverse('intelligence:ai_summarizer'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'AI News Summarizer')
        self.assertContains(res, 'Synthesize Summary')

    def test_ask_ai_page(self):
        res = self.client.get(reverse('intelligence:ask_ai'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'TrendBot AI')
        self.assertContains(res, 'What are today\'s top technology trends?')

    def test_login_and_logout(self):
        res = self.client.get(reverse('intelligence:login'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Terminal Access')

        # Post valid login
        post_res = self.client.post(reverse('intelligence:login'), {
            'username': 'test_analyst',
            'password': 'Password123!'
        })
        self.assertRedirects(post_res, reverse('intelligence:dashboard'))

        # Logout
        logout_res = self.client.get(reverse('intelligence:logout'))
        self.assertRedirects(logout_res, reverse('intelligence:index'))

    def test_register_page(self):
        res = self.client.get(reverse('intelligence:register'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Create Analyst Account')

    def test_forgot_password_page(self):
        res = self.client.get(reverse('intelligence:forgot_password'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Password Recovery')

    def test_profile_page(self):
        self.client.login(username='test_analyst', password='Password123!')
        res = self.client.get(reverse('intelligence:profile'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'User Profile & Analyst Settings')

    def test_saved_news_page(self):
        self.client.login(username='test_analyst', password='Password123!')
        res = self.client.get(reverse('intelligence:saved_news'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Saved Intelligence & Bookmarks')

    def test_api_summarize(self):
        # Short format
        res = self.client.post(
            reverse('intelligence:api_summarize'),
            data=json.dumps({
                'text': 'A major quantum computing milestone was achieved today. Physicists demonstrated non-Abelian Majorana braiding. This reduces error correction overhead significantly.',
                'format': 'short'
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('summary', data)

        # Key points format
        res_kp = self.client.post(
            reverse('intelligence:api_summarize'),
            data=json.dumps({
                'text': 'Tokamak fusion magnets reached 22 Tesla. Confinement lasted 72 hours.',
                'format': 'keypoints'
            }),
            content_type='application/json'
        )
        self.assertEqual(res_kp.status_code, 200)
        data_kp = res_kp.json()
        self.assertEqual(data_kp['format'], 'keypoints')

    def test_api_chat(self):
        res = self.client.post(
            reverse('intelligence:api_chat'),
            data=json.dumps({'message': 'What are today\'s top technology trends?'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('reply', data)

    def test_api_bookmark_toggle(self):
        self.client.login(username='test_analyst', password='Password123!')
        res = self.client.get(reverse('intelligence:api_bookmark_toggle', kwargs={'slug': self.article.slug}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['bookmarked'])
