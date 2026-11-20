import re
from django.utils import timezone
from news.models import NewsArticle, NewsCategory
from trends.models import TrendingTopic

class TrendBotService:
    """
    Interactive AI assistant for TRENDORA.
    Synthesizes conversational intelligence from real-time database dispatches
    and calculated trend models.
    """

    def process_message(self, user_message, user=None):
        msg = (user_message or '').strip().lower()

        if not msg:
            return {
                'response': "Greetings Analyst. I am TrendBot, TRENDORA's autonomous real-time intelligence assistant. Ask me about top tech trends, breaking dispatches, market momentum, or query specific keywords.",
                'suggestions': [
                    "What are today's top technology trends?",
                    "Summarize the latest business news.",
                    "What is happening in quantum computing?",
                    "Show breaking dispatches"
                ]
            }

        # Query Database for live state
        top_trends = list(TrendingTopic.objects.all().order_by('-calculated_score', '-velocity_percentage')[:5])
        latest_articles = list(NewsArticle.objects.all().order_by('-published_at')[:6])

        # 1. Tech Trends Query
        if any(w in msg for w in ['tech', 'technology', 'trends', 'top trend', 'popular']):
            tech_cat = NewsCategory.objects.filter(slug='technology').first()
            tech_trends = TrendingTopic.objects.filter(category__slug='technology').order_by('-calculated_score')[:4]
            if not tech_trends:
                tech_trends = top_trends[:4]

            lines = ["Here are today's highest-velocity technology intelligence trends:"]
            for idx, t in enumerate(tech_trends, 1):
                lines.append(f"**{idx}. {t.title}**")
                lines.append(f"• **Momentum**: {t.velocity_percentage:+d}% acceleration | **Score**: {t.calculated_score}/100")
                lines.append(f"• **Telemetry**: {t.volume_mentions:,} tracked mentions across {t.article_count} dispatches.")
                if t.summary:
                    lines.append(f"• *Briefing*: {t.summary}")
                lines.append("")

            related_art = NewsArticle.objects.filter(category__slug='technology').first()
            if related_art:
                lines.append(f"🔍 **Featured Dispatch**: *{related_art.title}* ({related_art.get_source_display()}) — Impact Index: {related_art.impact_score}/100.")

            return {
                'response': "\n".join(lines),
                'suggestions': [
                    "Deep-dive into Autonomous AI Agents",
                    "Summarize semiconductor fab progress",
                    "What are the top business headlines?",
                ]
            }

        # 2. Business & Economy Query
        elif any(w in msg for w in ['business', 'market', 'economy', 'financial', 'fed', 'stock']):
            biz_articles = list(NewsArticle.objects.filter(category__slug='business').order_by('-published_at')[:3])
            if not biz_articles:
                biz_articles = latest_articles[:3]

            lines = ["**Macroeconomic & Financial Intelligence Briefing:**\n"]
            for a in biz_articles:
                lines.append(f"• **{a.title}**")
                lines.append(f"  *Source*: {a.get_source_display()} | *Sentiment*: {a.sentiment} | *Velocity*: {a.velocity_score}")
                lines.append(f"  *Executive Summary*: {a.summary[:180]}...")
                lines.append("")

            lines.append("Key Takeaway: Capital markets are showing concentrated liquidity rotation toward sovereign atomic settlement and infrastructure efficiency.")
            return {
                'response': "\n".join(lines),
                'suggestions': [
                    "Explain sovereign digital reserves",
                    "Show latest technology headlines",
                    "What is trending in clean energy?",
                ]
            }

        # 3. Quantum Computing & AI
        elif any(w in msg for w in ['quantum', 'computing', 'ai', 'agent', 'model']):
            q_articles = list(NewsArticle.objects.filter(title__icontains='quantum').order_by('-published_at')[:2])
            ai_articles = list(NewsArticle.objects.filter(title__icontains='ai').order_by('-published_at')[:2])
            matched = q_articles + ai_articles
            if not matched:
                matched = latest_articles[:3]

            lines = ["**Frontier AI & Quantum Computing Intelligence:**\n"]
            for a in matched:
                lines.append(f"• **{a.title}** ({a.get_source_display()})")
                lines.append(f"  Impact Rating: {a.impact_score}/100 | Recency: {a.get_time_ago()}")
                lines.append(f"  {a.summary}")
                lines.append("")

            lines.append("Trendora Assessment: Hardware-software co-design between photonic quantum processors and multi-agent coordination frameworks is operating at peak inflection velocity.")
            return {
                'response': "\n".join(lines),
                'suggestions': [
                    "What are today's top technology trends?",
                    "How are solid-state batteries progressing?",
                    "Show breaking dispatches",
                ]
            }

        # 4. Breaking news dispatches
        elif any(w in msg for w in ['breaking', 'headline', 'latest', 'news', 'recent']):
            breaking = NewsArticle.objects.filter(is_breaking=True).order_by('-published_at')[:4]
            if not breaking:
                breaking = latest_articles[:4]

            lines = ["**Live Breaking Dispatches on the Grid:**\n"]
            for a in breaking:
                lines.append(f"⚡ **[{a.category.name.upper() if a.category else 'INTEL'}]** {a.title}")
                lines.append(f"   Wire: {a.get_source_display()} | Logged: {a.get_time_ago()} | Velocity: {a.velocity_score}")
                lines.append("")

            return {
                'response': "\n".join(lines),
                'suggestions': [
                    "Summarize top technology dispatch",
                    "What are today's top trends?",
                    "Analyze market sentiment",
                ]
            }

        # 5. General or Keyword Search fallback
        else:
            # Search database for keyword matches
            words = [w for w in re.findall(r'\w+', msg) if len(w) > 3]
            query_match = None
            for w in words:
                query_match = NewsArticle.objects.filter(title__icontains=w).first()
                if query_match:
                    break

            if query_match:
                response_text = (
                    f"**Intelligence telemetry for '{msg}':**\n\n"
                    f"Found primary match in dispatch: **{query_match.title}**\n"
                    f"• **Source**: {query_match.get_source_display()} ({query_match.get_time_ago()})\n"
                    f"• **Impact Index**: {query_match.impact_score}/100 | **Sentiment**: {query_match.sentiment}\n"
                    f"• **Summary**: {query_match.summary}\n\n"
                    f"Would you like me to generate a full executive briefing or track this topic's trajectory?"
                )
            else:
                top_3_str = ", ".join([f"**{t.title}** ({t.velocity_percentage:+d}%)" for t in top_trends[:3]])
                response_text = (
                    f"Analyst inquiry received: *\"{user_message}\"*\n\n"
                    f"TRENDORA is actively indexing 48,000+ real-time telemetry points. Currently, top momentum indicators are concentrated in {top_3_str}.\n\n"
                    f"You can ask me to summarize specific subjects, scan breaking dispatches, or evaluate sentiment across Technology, Business, Politics, Science, Sports, and Entertainment."
                )

            return {
                'response': response_text,
                'suggestions': [
                    "What are today's top technology trends?",
                    "Summarize the latest business news.",
                    "Show breaking dispatches",
                ]
            }
