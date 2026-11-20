import json
from django.test import TestCase, Client
from django.urls import reverse
from ai.services.summarizer_service import AiSummarizerService
from ai.services.trendbot_service import TrendBotService
from news.models import NewsCategory, NewsArticle
from trends.models import TrendingTopic

class AiIntelligenceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = NewsCategory.objects.create(
            name='Frontier Tech',
            slug='technology',
            icon='cpu'
        )
        self.topic = TrendingTopic.objects.create(
            title='Autonomous AI Agents',
            slug='autonomous-ai-agents',
            category=self.category,
            velocity_percentage=340,
            calculated_score=96.0
        )
        self.article = NewsArticle.objects.create(
            title='Next-Gen Quantum Processors Enter Commercial Fab Production',
            slug='next-gen-quantum-processors-commercial-fab',
            category=self.category,
            url='https://intel.trendora.io/dispatches/quantum-processors-commercial-fab',
            summary='Commercial fabrication milestone achieved for 128-qubit quantum microprocessors.',
            content='Semiconductor and quantum engineering consortium achieves multi-die photonic interconnect bonding.',
            impact_score=96
        )

    def test_summarizer_service_short_format(self):
        """Test AiSummarizerService returns structured short summary."""
        service = AiSummarizerService()
        raw_text = (
            "Autonomous multi-agent systems are transforming industrial software delivery. "
            "Recent benchmarks prove that self-coordinating agent swarms reduce code defects by 82%. "
            "Engineering organizations are transitioning from manual code reviews to formal automated verification loops."
        )
        res = service.summarize(text=raw_text, format_type='short')
        self.assertEqual(res['status'], 'success')
        self.assertEqual(res['format'], 'short')
        self.assertIn('Executive Synthesis', res['summary'])

    def test_summarizer_service_detailed_format(self):
        """Test AiSummarizerService returns comprehensive detailed briefing."""
        service = AiSummarizerService()
        raw_text = (
            "Central banks have unveiled atomic settlement protocols for foreign exchange reserves. "
            "The system relies on cryptographic multi-party threshold keys to authorize currency swaps in 1.4 seconds. "
            "Bilateral counterparty risk is effectively eliminated through mathematical delivery-versus-payment atomicity. "
            "Commercial banks project an annual liquidity saving of $42 billion across global trading desks. "
            "Regulatory frameworks are being harmonized across 24 sovereign monetary authorities."
        )
        res = service.summarize(text=raw_text, format_type='detailed')
        self.assertEqual(res['status'], 'success')
        self.assertEqual(res['format'], 'detailed')
        self.assertIn('Context & Core Catalyst', res['summary'])
        self.assertIn('Macroeconomic & Horizon Implications', res['summary'])

    def test_trendbot_service_technology_query(self):
        """Test TrendBot answers technology queries with live database telemetry."""
        bot = TrendBotService()
        result = bot.process_message("What are today's top technology trends?")
        self.assertIn('Autonomous AI Agents', result['response'])
        self.assertGreaterEqual(len(result['suggestions']), 1)

    def test_trendbot_service_business_query(self):
        """Test TrendBot answers business/economic queries."""
        bot = TrendBotService()
        result = bot.process_message("Summarize latest business news")
        self.assertIn('Macroeconomic', result['response'])

    def test_api_summarize_endpoint(self):
        """Test POST /api/summarize/ endpoint with JSON payload."""
        payload = {
            'text': 'High-NA EUV lithography achieves 8-nanometer pitch resolution on 300mm silicon wafers.',
            'format': 'short'
        }
        response = self.client.post(
            reverse('ai:api_summarize'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('summary', data)
        self.assertIn('words_original', data)

    def test_api_chat_endpoint(self):
        """Test POST /api/chat/ endpoint with message payload."""
        payload = {'message': "What are today's top technology trends?"}
        response = self.client.post(
            reverse('ai:api_chat'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('reply', data)
        self.assertIn('suggestions', data)
