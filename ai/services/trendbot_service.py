import re
import logging
from .rag_service import RagPipeline
from news.models import NewsCategory
from trends.models import TrendingTopic

logger = logging.getLogger('trendora.trendbot')

class TrendBotService:
    """
    TrendBot conversational intelligence service for TRENDORA.
    Orchestrates user inquiries through the RAG pipeline, retrieves relevant
    dispatches from FAISS, generates grounded citations via Groq LLM,
    and returns rich responses for the chat interface.
    """

    def __init__(self, rag_pipeline=None):
        self.rag = rag_pipeline or RagPipeline()

    def process_message(self, user_message, user=None, conversation_history=None):
        """
        Processes a natural language query through the RAG pipeline.
        Returns a structured dictionary with HTML reply, raw reply, citations, and suggestions.
        """
        msg = (user_message or '').strip()

        # Handle empty query
        if not msg:
            return {
                'reply': "Greetings Analyst. I am TrendBot, TRENDORA's autonomous real-time intelligence assistant. Ask me questions regarding latest technology breakthroughs, macroeconomic shifts, or query specific subjects.",
                'raw_reply': "Greetings Analyst. I am TrendBot.",
                'citations': [],
                'suggestions': [
                    "What are today's top technology trends?",
                    "Summarize recent semiconductor breakthroughs",
                    "What is happening in quantum computing?",
                    "Show breaking dispatches"
                ]
            }

        # Check for simple greetings
        if msg.lower() in ('hello', 'hi', 'hey', 'greetings', 'help'):
            top_trends = list(TrendingTopic.objects.all().order_by('-calculated_score')[:3])
            trend_names = ", ".join([f"**{t.title}** (+{t.velocity_percentage}%)" for t in top_trends])
            greeting = (
                f"Analyst terminal connected. TrendBot is actively monitoring 48,000+ signals. "
                f"Currently, top velocity indicators are concentrated in {trend_names or 'frontier computing'}.\n\n"
                f"What intelligence vector would you like to investigate?"
            )
            return {
                'reply': greeting.replace('\n\n', '<br><br>'),
                'raw_reply': greeting,
                'citations': [],
                'suggestions': [
                    "What are today's top technology trends?",
                    "Summarize recent semiconductor breakthroughs",
                    "Explain sovereign digital reserves",
                ]
            }

        # Run through RAG Pipeline
        try:
            rag_result = self.rag.run_rag(
                query=msg,
                top_k=4,
                conversation_history=conversation_history
            )

            raw_answer = rag_result.get('answer', '')
            citations = rag_result.get('citations', [])

            # Format raw markdown answer into HTML for chat bubbles
            html_reply = raw_answer.replace('\n\n', '<br><br>').replace('\n', '<br>')
            html_reply = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_reply)
            html_reply = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_reply)
            html_reply = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank" style="color:var(--cyan-accent); text-decoration:underline;">\1</a>', html_reply)

            # Generate smart suggestions based on retrieved categories or topics
            suggestions = self._generate_suggestions(msg, citations)

            return {
                'reply': html_reply,
                'raw_reply': raw_answer,
                'citations': citations,
                'suggestions': suggestions,
                'context_count': rag_result.get('context_count', 0),
            }

        except Exception as e:
            logger.error(f"Error in TrendBot RAG execution: {e}", exc_info=True)
            fallback_msg = (
                "An anomaly occurred in the intelligence telemetry buffer. "
                "The core neural inference pipeline is reconnecting to the primary wire. "
                "Please retry your inquiry in a few seconds."
            )
            return {
                'reply': fallback_msg,
                'raw_reply': fallback_msg,
                'citations': [],
                'suggestions': [
                    "What are today's top technology trends?",
                    "Show breaking dispatches",
                ]
            }

    def _generate_suggestions(self, query, citations):
        """Generates dynamic follow-up suggestions based on query keywords or citations."""
        suggestions = []
        if citations:
            first_cit = citations[0]['title']
            suggestions.append(f"Deep-dive into {first_cit[:35]}...")
        
        low = query.lower()
        if 'ai' in low or 'agent' in low:
            suggestions.append("What are the hardware bottlenecks for autonomous agents?")
            suggestions.append("Summarize semiconductor fab progress")
        elif 'quantum' in low:
            suggestions.append("Explain quantum error correction milestones")
            suggestions.append("What are top science trends?")
        elif 'business' in low or 'market' in low:
            suggestions.append("What are sovereign digital reserve trends?")
            suggestions.append("Show breaking financial dispatches")
        else:
            suggestions.append("What are today's top technology trends?")
            suggestions.append("Summarize breaking news dispatches")

        return suggestions[:3]
