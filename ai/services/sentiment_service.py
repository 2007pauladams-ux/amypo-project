import json
import logging
from django.conf import settings
from .groq_service import GroqService
from news.models import NewsArticle

logger = logging.getLogger('trendora.sentiment')

DISCLAIMER_TEXT = "Analytical Disclaimer: Sentiment classification reflects reporting tone and journalistic framing within the evaluated dispatches; it does not constitute proof of real-world outcome, financial advice, or geopolitical certainty."

class SentimentAnalysisService:
    """
    Sentiment Analysis Engine for TRENDORA.
    Classifies article content into BULLISH, BEARISH, HIGH IMPACT, or NEUTRAL,
    generates confidence metrics and explicit explanations, and updates the database.
    """

    def __init__(self, groq_service=None):
        self.groq_service = groq_service or GroqService()

    def analyze_text(self, title, text=""):
        """
        Analyzes a title and text payload for sentiment.
        Returns dict with sentiment, confidence, explanation, and disclaimer.
        """
        content = f"Title: {title}\nText: {text[:1500]}"

        system_prompt = (
            "You are an objective sentiment analysis engine for TRENDORA Intelligence.\n"
            "Classify the provided news article content into exactly one of four sentiment classifications:\n"
            "1. BULLISH (positive technological expansion, breakthroughs, efficiency gains, market optimism)\n"
            "2. BEARISH (contraction, security vulnerabilities, failures, regulatory penalties, decline)\n"
            "3. HIGH IMPACT (paradigm shift, critical treaties, unprecedented breakthrough with disruptive ramifications)\n"
            "4. NEUTRAL (routine reporting, steady state, factual procedural update)\n\n"
            "Return valid JSON strictly matching this schema:\n"
            "{\n"
            "  \"sentiment\": \"BULLISH\" | \"BEARISH\" | \"HIGH IMPACT\" | \"NEUTRAL\",\n"
            "  \"confidence\": 0.92,\n"
            "  \"explanation\": \"Brief 1-2 sentence explanation citing specific keywords or phrases from the text.\"\n"
            "}"
        )

        user_prompt = f"Evaluate the sentiment of this dispatch:\n\n{content}"

        raw_resp = self.groq_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=250
        )

        try:
            # Extract JSON block
            json_str = raw_resp
            if '{' in raw_resp and '}' in raw_resp:
                start = raw_resp.find('{')
                end = raw_resp.rfind('}') + 1
                json_str = raw_resp[start:end]
            data = json.loads(json_str)

            sentiment = data.get("sentiment", "HIGH IMPACT").upper()
            if sentiment not in ("BULLISH", "BEARISH", "HIGH IMPACT", "NEUTRAL", "DEVELOPING"):
                sentiment = "HIGH IMPACT"

            confidence = float(data.get("confidence", 0.88))
            explanation = data.get("explanation", "Sentiment derived from structural terminology and momentum indicators.")

            return {
                'status': 'success',
                'sentiment': sentiment,
                'confidence': confidence,
                'explanation': explanation,
                'disclaimer': DISCLAIMER_TEXT,
            }
        except Exception as e:
            logger.warning(f"Error parsing sentiment JSON: {e}. Using deterministic heuristic.")
            return self._heuristic_sentiment(title, text)

    def analyze_and_update_article(self, article_id):
        """
        Analyzes a NewsArticle in the database and updates its sentiment field.
        """
        article = NewsArticle.objects.filter(id=article_id).first()
        if not article:
            return {'status': 'error', 'message': 'Article not found.'}

        result = self.analyze_text(article.title, f"{article.summary} {article.content}")
        
        # Update model
        article.sentiment = result['sentiment']
        article.save(update_fields=['sentiment'])

        result['article_id'] = article.id
        result['article_title'] = article.title
        return result

    def _heuristic_sentiment(self, title, text):
        """Fallback deterministic heuristic classifier."""
        combined = f"{title} {text}".lower()
        bullish_words = ['breakthrough', 'record', 'surge', 'surpass', 'outperform', 'gain', 'efficiency', 'positive', 'commercial']
        bearish_words = ['vulnerability', 'breach', 'fall', 'fail', 'decline', 'loss', 'halt', 'probe', 'ban', 'risk', 'crisis']
        impact_words = ['quantum', 'ignite', 'treaty', 'accord', 'transform', 'revolution', 'sovereign', 'lithography']

        b_count = sum(1 for w in bullish_words if w in combined)
        bear_count = sum(1 for w in bearish_words if w in combined)
        imp_count = sum(1 for w in impact_words if w in combined)

        if bear_count > b_count and bear_count > 0:
            sentiment = "BEARISH"
            exp = "Detected risk and contraction terminology in text body."
        elif imp_count >= 2:
            sentiment = "HIGH IMPACT"
            exp = "Detected transformative frontier terminology and paradigm indicators."
        elif b_count > 0:
            sentiment = "BULLISH"
            exp = "Detected technological milestone and efficiency indicators."
        else:
            sentiment = "NEUTRAL"
            exp = "Standard baseline intelligence reporting without extreme polarization."

        return {
            'status': 'success',
            'sentiment': sentiment,
            'confidence': 0.85,
            'explanation': exp,
            'disclaimer': DISCLAIMER_TEXT,
        }
