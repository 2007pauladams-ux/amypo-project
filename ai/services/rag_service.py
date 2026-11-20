import logging
from django.conf import settings
from .groq_service import GroqService
from .vector_store import FaissVectorStore
from news.models import NewsArticle

logger = logging.getLogger('trendora.rag')

class RagPipeline:
    """
    Retrieval-Augmented Generation (RAG) pipeline for TRENDORA.
    Orchestrates semantic vector retrieval via FAISS and context-grounded
    generation via the Groq LLM API with strict citation requirements and
    anti-hallucination guardrails.
    """

    def __init__(self, vector_store=None, groq_service=None):
        self.vector_store = vector_store or FaissVectorStore()
        self.groq_service = groq_service or GroqService()

    def run_rag(self, query, top_k=4, min_score=0.10, conversation_history=None):
        """
        Executes the RAG cycle for a user query.
        Returns a structured dictionary with answer, citations, and metrics.
        """
        cleaned_query = (query or '').strip()
        if not cleaned_query:
            return {
                'status': 'error',
                'message': 'Query cannot be empty.',
                'answer': 'Please provide an intelligence query or topic to analyze.',
                'citations': [],
                'context_count': 0
            }

        # 1. Ensure FAISS has articles indexed
        if self.vector_store.count() == 0:
            logger.info("FAISS vector store is empty; auto-indexing from database...")
            self.vector_store.rebuild_index_from_db()

        # 2. Retrieve top-k relevant articles from FAISS
        raw_results = self.vector_store.search(cleaned_query, top_k=top_k)

        # Fallback to text match if vector search yielded zero results
        if not raw_results:
            db_matches = NewsArticle.objects.filter(title__icontains=cleaned_query)[:top_k]
            for a in db_matches:
                raw_results.append((a.id, 0.85, {
                    'id': a.id,
                    'title': a.title,
                    'slug': a.slug,
                    'source_name': a.get_source_display(),
                    'url': a.url,
                    'impact_score': a.impact_score,
                }))

        # 3. Anti-hallucination filter: check for empty or completely irrelevant context
        filtered_results = [r for r in raw_results if r[1] >= min_score]

        if not filtered_results:
            return {
                'status': 'no_context',
                'answer': (
                    f"No verified intelligence dispatches matching **'{cleaned_query}'** were identified "
                    f"in the TRENDORA database. In accordance with platform protocols, TrendBot synthesizes "
                    f"only verified incoming telemetry and does not extrapolate or generate ungrounded claims."
                ),
                'citations': [],
                'context_count': 0,
                'query': cleaned_query,
            }

        # 4. Resolve article records and compile context
        article_ids = [r[0] for r in filtered_results]
        article_map = {a.id: a for a in NewsArticle.objects.filter(id__in=article_ids).select_related('category', 'source')}

        context_blocks = []
        citations = []

        for rank, (aid, score, meta) in enumerate(filtered_results, 1):
            article = article_map.get(aid)
            title = article.title if article else meta.get('title', 'Unknown Dispatch')
            source = article.get_source_display() if article else meta.get('source_name', 'Global Wire')
            url = article.url if article else meta.get('url', '')
            slug = article.slug if article else meta.get('slug', '')
            summary = article.summary if article else 'Summary briefing unavailable.'
            content = article.content[:600] if article else summary
            impact = article.impact_score if article else meta.get('impact_score', 85)

            context_blocks.append(
                f"[Dispatch #{rank}]\n"
                f"Title: {title}\n"
                f"Source: {source} (Impact Index: {impact}/100)\n"
                f"URL: {url}\n"
                f"Executive Briefing: {summary}\n"
                f"Report Details: {content}\n"
            )

            citations.append({
                'id': aid,
                'title': title,
                'slug': slug,
                'source_name': source,
                'url': url,
                'similarity_score': round(score, 3),
                'impact_score': impact,
            })

        context_text = "\n\n".join(context_blocks)

        # 5. Build strict Grounded Prompt
        system_prompt = (
            "You are TrendBot, the autonomous intelligence analyst AI for TRENDORA.\n"
            "Your objective is to answer the user query accurately, concisely, and objectively using "
            "ONLY the verified dispatch context supplied below.\n\n"
            "STRICT GROUNDING RULES:\n"
            "1. Answer based ONLY on the supplied dispatches. Never invent, hallucinate, or assume unverified facts.\n"
            "2. Cite sources explicitly using article titles, publication wires, and URLs.\n"
            "3. If the context does not fully answer all aspects of the inquiry, clearly state that specific verified intelligence is currently unavailable.\n"
            "4. Format your output cleanly with markdown headings, bullet points, and an explicit 'Verified Citations' list at the bottom."
        )

        user_prompt = (
            f"VERIFIED DISPATCH CONTEXT:\n"
            f"----------------------------------------\n"
            f"{context_text}\n"
            f"----------------------------------------\n\n"
            f"USER QUERY: {cleaned_query}\n\n"
            f"Synthesize an executive intelligence briefing answering the user query using only the above context."
        )

        # 6. Invoke Groq LLM
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history and isinstance(conversation_history, list):
            for hist in conversation_history[-3:]:
                if 'role' in hist and 'content' in hist:
                    messages.append(hist)
        messages.append({"role": "user", "content": user_prompt})

        llm_response = self.groq_service.chat(
            messages=messages,
            temperature=0.2,
            max_tokens=1500
        )

        # 7. Format citations into response if missing
        if "Citations" not in llm_response and citations:
            citation_links = "\n\n**Verified Intelligence Citations:**\n" + "\n".join([
                f"• [{c['title']}]({c['url']}) — *{c['source_name']}* (Impact: {c['impact_score']}/100)"
                for c in citations
            ])
            llm_response += citation_links

        return {
            'status': 'success',
            'answer': llm_response,
            'citations': citations,
            'context_count': len(citations),
            'query': cleaned_query,
        }
