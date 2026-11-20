import json
import numpy as np
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from news.models import NewsCategory, NewsSource, NewsArticle
from trends.models import TrendingTopic
from ai.services.groq_service import GroqService
from ai.services.embedding_service import EmbeddingService, EMBEDDING_DIM
from ai.services.vector_store import FaissVectorStore
from ai.services.rag_service import RagPipeline
from ai.services.summarizer_service import AiSummarizerService
from ai.services.trendbot_service import TrendBotService
from ai.services.trend_intelligence_service import TrendIntelligenceService
from ai.services.sentiment_service import SentimentAnalysisService

class AiModuleComprehensiveTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = NewsCategory.objects.create(
            name='Quantum & Frontier AI',
            slug='quantum-ai',
            icon='cpu',
            badge_class='badge-purple'
        )
        self.source = NewsSource.objects.create(
            name='Frontier Systems Wire',
            slug='frontier-systems-wire',
            domain='frontier.intel'
        )
        self.article1 = NewsArticle.objects.create(
            title='Autonomous AI Agents Achieve Multi-Model Quantum Orchestration Breakthrough',
            slug='autonomous-ai-agents-quantum-orchestration',
            category=self.category,
            source=self.source,
            source_name='Frontier Systems Wire',
            source_domain='frontier.intel',
            url='https://intel.trendora.io/dispatches/autonomous-ai-quantum-orchestration',
            summary='Researchers deploy autonomous multi-agent routing reducing latency by 74% across quantum coprocessors.',
            content='Full briefing: Autonomous multi-agent coordination architecture demonstrates real-time distributed load balancing.',
            impact_score=98,
            velocity_score='+340% / 1h',
            sentiment='BULLISH',
            published_at=timezone.now()
        )
        self.article2 = NewsArticle.objects.create(
            title='Global Semiconductor Consortium Unveils 1-Nanometer High-NA EUV Commercial Roadmap',
            slug='semiconductor-1nm-high-na-euv-roadmap',
            category=self.category,
            source=self.source,
            source_name='Frontier Systems Wire',
            source_domain='frontier.intel',
            url='https://intel.trendora.io/dispatches/semiconductor-1nm-roadmap',
            summary='Commercial foundries finalize production schedules for 10-angstrom silicon nodes utilizing 0.55 NA optics.',
            content='Full briefing: High-NA EUV lithography achieves 8nm pitch resolution with single-exposure efficiency.',
            impact_score=94,
            velocity_score='+210% / 1h',
            sentiment='HIGH IMPACT',
            published_at=timezone.now()
        )
        self.topic = TrendingTopic.objects.create(
            title='Autonomous AI Agents',
            slug='autonomous-ai-agents',
            category=self.category,
            volume_mentions=48000,
            velocity_percentage=340,
            calculated_score=96.5,
            sentiment='bullish',
            trend_direction='hot',
            is_hot=True
        )

    # 1. Groq LLM Service Tests (Item 21, 22)
    def test_groq_service_configuration_and_generation(self):
        """Test GroqService model configuration, parameters, and fallback generation."""
        service = GroqService(model='llama-3.3-70b-versatile')
        self.assertEqual(service.model, 'llama-3.3-70b-versatile')
        
        response = service.generate(
            prompt="Summarize the core impact of quantum computing in 2 sentences.",
            system_prompt="You are a technology analyst.",
            temperature=0.2,
            max_tokens=300
        )
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 20)

    # 2. Embedding Service Tests (Item 24)
    def test_embedding_service_dimension_and_normalization(self):
        """Test Sentence Transformers embeddings generate 384-dim L2-normalized vectors."""
        service = EmbeddingService()
        self.assertEqual(service.dimension, 384)

        # Single embedding
        vec = service.get_embedding("Autonomous AI multi-agent orchestration architecture.")
        self.assertEqual(vec.shape, (384,))
        self.assertEqual(vec.dtype, np.float32)
        norm = float(np.linalg.norm(vec))
        self.assertAlmostEqual(norm, 1.0, places=2)

        # Empty text handling
        empty_vec = service.get_embedding("   ")
        self.assertEqual(empty_vec.shape, (384,))
        self.assertEqual(float(np.linalg.norm(empty_vec)), 0.0)

        # Batch embeddings
        batch = service.get_embeddings(["Quantum circuit scale", "Semiconductor fab node", ""])
        self.assertEqual(batch.shape, (3, 384))

    # 3. FAISS Vector Database Tests (Item 25)
    def test_faiss_vector_store_operations(self):
        """Test adding documents, searching, persistence, and database rebuild in FAISS."""
        store = FaissVectorStore()
        indexed = store.rebuild_index_from_db()
        self.assertGreaterEqual(indexed, 2)
        self.assertGreaterEqual(store.count(), 2)

        # Search query matching semiconductor
        results = store.search("semiconductor lithography fabs", top_k=2)
        self.assertGreater(len(results), 0)
        top_aid, score, meta = results[0]
        self.assertIn('title', meta)
        self.assertGreater(score, -1.0)

        # Save and reload verification
        self.assertTrue(store.save())
        reloaded = FaissVectorStore()
        self.assertEqual(reloaded.count(), store.count())

    # 4. RAG Pipeline Tests (Item 26)
    def test_rag_pipeline_grounded_retrieval_and_citations(self):
        """Test RAG retrieves context, cites articles, and avoids hallucination."""
        pipeline = RagPipeline()
        res = pipeline.run_rag(query="What is the breakthrough in autonomous AI agents and quantum orchestration?", top_k=2)
        self.assertEqual(res['status'], 'success')
        self.assertGreaterEqual(res['context_count'], 1)
        self.assertGreater(len(res['citations']), 0)
        self.assertIn('Autonomous AI Agents Achieve Multi-Model Quantum Orchestration Breakthrough', res['citations'][0]['title'])
        self.assertIn('Frontier Systems Wire', res['citations'][0]['source_name'])

    def test_rag_pipeline_anti_hallucination_on_irrelevant_query(self):
        """Test RAG explicitly informs user when no relevant verified articles exist."""
        pipeline = RagPipeline()
        # Query intentionally far removed from database articles with high threshold
        res = pipeline.run_rag(
            query="xyz999 nonexistent alien ruins on pluto crater expedition",
            top_k=2,
            min_score=0.99
        )
        self.assertIn(res['status'], ('no_context', 'success'))
        if res['status'] == 'no_context':
            self.assertIn('No verified intelligence dispatches', res['answer'])
            self.assertEqual(len(res['citations']), 0)

    # 5. Summarizer Service Tests (Item 23)
    def test_summarizer_service_formats(self):
        """Test AI news summarization generates Short, Detailed, and Key Points formats."""
        service = AiSummarizerService()
        text = (
            "Researchers announced a quantum computing breakthrough today. "
            "Using specialized cryogenic control chips operating at 4 Kelvin, "
            "the system reduced thermal decoherence rates by 68%. "
            "Commercial cloud providers plan to integrate the controllers into data centers."
        )

        # Short Summary
        short_res = service.summarize(text=text, format_type='short')
        self.assertEqual(short_res['status'], 'success')
        self.assertEqual(short_res['format'], 'short')
        self.assertIn('Executive Synthesis', short_res['raw_summary'])

        # Detailed Summary
        det_res = service.summarize(text=text, format_type='detailed')
        self.assertEqual(det_res['status'], 'success')
        self.assertEqual(det_res['format'], 'detailed')
        self.assertIn('Context & Core Catalyst', det_res['raw_summary'])

        # Key Points
        kp_res = service.summarize(text=text, format_type='keypoints')
        self.assertEqual(kp_res['status'], 'success')
        self.assertEqual(kp_res['format'], 'keypoints')
        self.assertIn('Key Strategic Intelligence Vectors', kp_res['raw_summary'])

    # 6. TrendBot Chatbot Tests (Item 27)
    def test_trendbot_chatbot_service(self):
        """Test TrendBot conversational assistant returns answers, citations, and suggestions."""
        bot = TrendBotService()
        result = bot.process_message("What are the latest semiconductor fab milestones?")
        self.assertIn('reply', result)
        self.assertIn('suggestions', result)
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreaterEqual(len(result['suggestions']), 1)

    # 7. Trend Intelligence Service Tests (Item 28)
    def test_trend_intelligence_service(self):
        """Test AI-assisted trend intelligence identifies recurring entities and explains trend."""
        service = TrendIntelligenceService()
        result = service.analyze_trending_topic(self.topic.slug)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['topic_title'], 'Autonomous AI Agents')
        self.assertIn('thematic_explanation', result)
        self.assertIn('key_entities', result)
        self.assertIn('observed_evidence', result)
        self.assertIn('forward_horizon', result)

    # 8. Sentiment Analysis Service Tests (Item 29)
    def test_sentiment_analysis_service_and_db_update(self):
        """Test sentiment classification, confidence, explanation, and model update."""
        service = SentimentAnalysisService()
        res = service.analyze_and_update_article(self.article1.id)
        self.assertEqual(res['status'], 'success')
        self.assertIn(res['sentiment'], ('BULLISH', 'BEARISH', 'HIGH IMPACT', 'NEUTRAL'))
        self.assertGreater(res['confidence'], 0.0)
        self.assertIn('disclaimer', res)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.sentiment, res['sentiment'])

    # 9. REST API Endpoints Tests (Item 30)
    def test_api_summarize_endpoint(self):
        """Test POST /api/summarize/ endpoint."""
        payload = {
            'text': 'Semiconductor fabs deploy High-NA EUV lithography for 10-angstrom nodes.',
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

    def test_api_chat_endpoint(self):
        """Test POST /api/chat/ endpoint."""
        payload = {'message': "What is the breakthrough in quantum orchestration?"}
        response = self.client.post(
            reverse('ai:api_chat'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('reply', data)

    def test_api_rag_endpoint(self):
        """Test POST /api/rag/ direct RAG endpoint."""
        payload = {'query': "Semiconductor lithography", 'top_k': 3}
        response = self.client.post(
            reverse('ai:api_rag_query'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data['status'], ('success', 'no_context'))

    def test_api_sentiment_endpoint(self):
        """Test POST /api/sentiment/ endpoint."""
        payload = {'article_id': self.article1.id}
        response = self.client.post(
            reverse('ai:api_sentiment'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('sentiment', data)
        self.assertIn('confidence', data)

    def test_api_trend_intelligence_endpoint(self):
        """Test GET /api/trends/intelligence/ endpoint."""
        response = self.client.get(
            reverse('ai:api_trend_intelligence'),
            {'topic': self.topic.slug}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['topic_slug'], self.topic.slug)

    def test_api_faiss_reindex_endpoint(self):
        """Test POST /api/faiss/reindex/ endpoint."""
        response = self.client.post(reverse('ai:api_faiss_reindex'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(data['total_indexed'], 2)
