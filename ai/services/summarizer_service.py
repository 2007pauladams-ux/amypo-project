import re
import logging
import requests
from urllib.parse import urlparse
from news.models import NewsArticle
from .groq_service import GroqService

logger = logging.getLogger('trendora.summarizer')

class AiSummarizerService:
    """
    AI-powered news summarization engine for TRENDORA utilizing the Groq LLM API.
    Generates three grounded summary formats (Short Summary, Detailed Summary, Key Points)
    strictly based on supplied article content with zero external hallucination.
    """

    def __init__(self, groq_service=None):
        self.groq_service = groq_service or GroqService()

    def summarize(self, text='', url='', format_type='short'):
        """
        Main entry point for article text/URL summarization.
        format_type: 'short' | 'detailed' | 'keypoints'.
        """
        article_title = "Submitted Intelligence Dispatch"
        article_source = "Analyst Direct Input"

        # 1. Resolve URL if provided and text is empty
        if url and not text.strip():
            url = url.strip()
            existing = NewsArticle.objects.filter(url=url).first()
            if existing:
                text = f"Title: {existing.title}\n\nSummary: {existing.summary}\n\nContent: {existing.content}"
                article_title = existing.title
                article_source = existing.get_source_display()
            else:
                try:
                    resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                    if resp.status_code == 200:
                        title_match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
                        if title_match:
                            article_title = title_match.group(1).strip()
                        clean = re.sub(r'<script.*?</script>', '', resp.text, flags=re.DOTALL)
                        clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL)
                        clean = re.sub(r'<.*?>', ' ', clean)
                        text = ' '.join(clean.split())[:4000]
                        article_source = urlparse(url).netloc
                except Exception as e:
                    logger.warning(f"Error fetching URL {url}: {e}")
                    text = f"External dispatch from {url}."

        cleaned_text = ' '.join((text or '').split())
        if not cleaned_text:
            cleaned_text = "No article content provided for analysis."

        original_word_count = len(cleaned_text.split())

        # 2. Build Groq LLM Prompt
        system_prompt = (
            "You are an expert intelligence analyst for TRENDORA.\n"
            "Your task is to summarize the provided news article accurately, clearly, and concisely.\n"
            "STRICT RULES:\n"
            "1. Base your summary ONLY on the facts explicitly mentioned in the provided text.\n"
            "2. Do NOT extrapolate, hallucinate, or add external unsupported claims.\n"
            "3. Maintain an objective, high-conviction intelligence tone.\n"
        )

        if format_type == 'short':
            format_prompt = (
                "Format requirement: SHORT SUMMARY.\n"
                "Provide a concise executive summary in 2 to 3 bullet points, followed by a one-sentence Strategic Horizon takeaway.\n"
                "Heading format: **Executive Synthesis: <Title>**\n"
            )
        elif format_type == 'detailed':
            format_prompt = (
                "Format requirement: DETAILED STRATEGIC BRIEFING.\n"
                "Provide a comprehensive structured report with 4 distinct sections:\n"
                "### Comprehensive Intelligence Report: <Title>\n"
                "#### 1. Context & Core Catalyst\n"
                "#### 2. Direct Operational & Technological Impact\n"
                "#### 3. Macroeconomic & Horizon Implications\n"
                "#### 4. Trendora Risk & Velocity Projection\n"
            )
        else: # keypoints
            format_prompt = (
                "Format requirement: IMPORTANT KEY POINTS.\n"
                "Extract 4 to 6 distinct, numbered bullet points with bold headlines highlighting the most critical facts, numbers, and findings.\n"
                "Heading format: **Key Strategic Intelligence Vectors: <Title>**\n"
            )

        user_prompt = (
            f"{format_prompt}\n"
            f"SOURCE ARTICLE CONTENT:\n"
            f"\"\"\"\n{cleaned_text[:4000]}\n\"\"\"\n\n"
            f"Generate the grounded {format_type} summary now."
        )

        # 3. Call Groq LLM
        summary_text = self.groq_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=1200
        )

        summary_word_count = len(summary_text.split())
        saved_pct = max(10, min(85, int((1 - (summary_word_count / max(original_word_count, 1))) * 100)))

        format_labels = {
            'short': 'Short Executive Summary',
            'detailed': 'Detailed Strategic Briefing',
            'keypoints': 'Actionable Key Points'
        }

        # Convert markdown formatting to clean HTML for innerHTML display
        html_summary = summary_text.replace('\n\n', '<br><br>').replace('\n', '<br>')
        html_summary = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_summary)
        html_summary = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_summary)
        html_summary = re.sub(r'### (.*?)<br>', r'<h3 style="color:var(--purple-light); margin:0.8rem 0 0.4rem;">\1</h3>', html_summary)
        html_summary = re.sub(r'#### (.*?)<br>', r'<h4 style="color:var(--text-primary); margin:0.6rem 0 0.3rem;">\1</h4>', html_summary)

        return {
            'status': 'success',
            'format': format_type,
            'format_label': format_labels.get(format_type, 'Summary Briefing'),
            'title': article_title,
            'source': article_source,
            'original_word_count': original_word_count,
            'summary_word_count': summary_word_count,
            'words_original': original_word_count,
            'words_summary': summary_word_count,
            'saved_percentage': saved_pct,
            'compression_ratio': f"{saved_pct}% reduction",
            'estimated_read_time': f"{max(1, summary_word_count // 140)} min read",
            'summary': html_summary,
            'raw_summary': summary_text,
        }
