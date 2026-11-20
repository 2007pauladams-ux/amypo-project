# TRENDORA — Frontend Routes & Backend API Specifications

This document outlines all frontend user-facing routes, reusable Django template components, and expected backend API endpoints for the **TRENDORA — Real-Time News and Trend Intelligence** platform.

---

## 1. Frontend Web Routes

| Route | View Function | App & Namespace | Template | Description |
|---|---|---|---|---|
| `/` | `news_views.index_view` | `news:index` | `templates/intelligence/index.html` | Primary homepage with hero radar, prominent news search bar, breakthrough spotlight story, telemetry cards, and live dispatches feed. |
| `/dashboard/` | `news_views.dashboard_view` | `news:dashboard` | `templates/intelligence/dashboard.html` | Comprehensive analyst dashboard with left command sidebar, KPI metrics, hot trending keywords, recent articles, and domain matrix sections. |
| `/search/` | `news_views.advanced_search_view` | `news:advanced_search` | `templates/intelligence/search.html` | Advanced intelligence search interface with large search bar, trending query tags, domain/date/source/relevance filters, and interactive card results. |
| `/trending/` | `trends_views.trending_topics_view` | `trends:trending` | `templates/intelligence/trending.html` | Dedicated Trending Topics page spanning Technology, Business, Politics, Sports, Science, Entertainment with momentum meters, sparklines, and signal counts. |
| `/summarizer/` | `ai_views.summarizer_view` | `ai:ai_summarizer` | `templates/intelligence/summarizer.html` | AI News Summarizer interface accepting article URL or raw text with Short, Detailed, and Key Points formats, loading states, and clipboard copy. |
| `/ask-ai/` | `ai_views.ask_ai_view` | `ai:ask_ai` | `templates/intelligence/ask_ai.html` | TrendBot interactive conversational AI assistant with preset inquiries, typing indicators, live chat bubbles, and auto-scroll. |
| `/login/` | `accounts_views.login_view` | `accounts:login` | `templates/auth/login.html` | Secure terminal login with CSRF protection, password visibility toggle, error handling, and demo account credentials. |
| `/register/` | `accounts_views.register_view` | `accounts:register` | `templates/auth/register.html` | New analyst registration page with validation, password confirmation, and automatic profile creation. |
| `/logout/` | `accounts_views.logout_view` | `accounts:logout` | *Redirects to `/`* | Closes user session and redirects to homepage with feedback toast. |
| `/forgot-password/` | `accounts_views.forgot_password_view` | `accounts:forgot_password` | `templates/auth/forgot_password.html` | Password recovery interface for requesting reset tokens. |
| `/profile/` | `accounts_views.profile_view` | `accounts:profile` | `templates/intelligence/profile.html` | Analyst profile management, editable username/email/bio, domain preference checkboxes, and activity counters. |
| `/saved/` | `news_views.saved_news_view` | `news:saved_news` | `templates/intelligence/saved_news.html` | Dedicated saved intelligence library displaying user bookmarks with one-click remove and clear actions. |

---

## 2. Reusable Django Template Components

Located in `templates/components/`:

### A. Regular News Card
- **File**: `templates/components/news_card.html`
- **Usage**:
  ```django
  {% include 'components/news_card.html' with article=article %}
  ```
- **Features**: Visual thumbnail banner with gradient & geometric pattern, category tag, impact score badge, headline, source wire dot, publication date, summary, sentiment pill, reading time, "Analyze Signal" drawer trigger, and bookmark toggle.

### B. Featured Breakthrough Card
- **File**: `templates/components/news_card_featured.html`
- **Usage**:
  ```django
  {% include 'components/news_card_featured.html' with article=featured_article %}
  ```
- **Features**: Dual-column layout, animated rotating radar scan, dynamic Impact Score Gauge (`1-100`), Trend Velocity badge (`+340% / 1h`), executive synthesis bullet points, and drawer report launcher.

### C. Compact News Card
- **File**: `templates/components/news_card_compact.html`
- **Usage**:
  ```django
  {% include 'components/news_card_compact.html' with article=article %}
  ```
- **Features**: Dense horizontal strip for dashboards and sidebar widgets, showing domain pill, relative timestamp, headline, source name, and impact star.

---

## 3. Backend REST & AJAX API Endpoints

### A. Articles Stream Query
- **Endpoint**: `GET /api/articles/`
- **Query Parameters**:
  - `q` (string, optional): Search keyword query matching title, summary, content, source, or author.
  - `category` (string, optional): Category slug (`technology`, `business`, `politics`, `sports`, `science`, `entertainment`).
  - `source` (string, optional): Source slug or ID.
  - `sort` (string, optional): `latest` (default), `impact`, `velocity`.
  - `page` (integer, optional): Current page number (default: 1).
  - `page_size` (integer, optional): Items per page (default: 12, max: 50).
- **Response Format**:
  ```json
  {
    "status": "success",
    "count": 18,
    "num_pages": 2,
    "current_page": 1,
    "has_next": true,
    "has_previous": false,
    "articles": [
      {
        "id": 1,
        "title": "Autonomous Multi-Agent Networks Surpass Human Engineering Velocity in Hardware Simulation",
        "slug": "autonomous-multi-agent-networks-surpass-human-velocity",
        "category_id": 1,
        "category_name": "Technology & Computing",
        "category_slug": "technology",
        "category_color": "#8b5cf6",
        "category_badge": "badge-purple",
        "source_name": "MIT Technology Review",
        "source_domain": "technologyreview.com",
        "published_at": "2026-11-20T14:45:00Z",
        "formatted_date": "Nov 20, 2026",
        "time_ago": "18m ago",
        "summary": "Hierarchical agent swarms autonomously verify complex verilog silicon circuits...",
        "content": "A benchmark release from frontier compute teams...",
        "takeaways": [
          "Autonomous multi-agent swarms achieve 14x acceleration in silicon circuit timing verification.",
          "Direct reduction of multi-month chip physical design cycles to under 72 hours."
        ],
        "read_time_minutes": 5,
        "impact_score": 98,
        "velocity_score": "+340% / 1h",
        "sentiment": "BULLISH",
        "image_gradient": "linear-gradient(135deg, #1e1b4b 0%, #311042 100%)",
        "hero_pattern": "neural-grid",
        "is_featured": true,
        "is_breaking": true,
        "views_count": 1420
      }
    ]
  }
  ```

### B. Single Article Detail
- **Endpoint**: `GET /api/articles/<slug>/`
- **Response Format**:
  ```json
  {
    "status": "success",
    "article": { ... }
  }
  ```

### C. Article Bookmark Toggle
- **Endpoint**: `POST /api/bookmark/<slug>/`
- **Authentication**: Authenticated user session (or fallback to demo session).
- **Response Format**:
  ```json
  {
    "status": "success",
    "action": "saved",
    "is_saved": true,
    "slug": "autonomous-multi-agent-networks-surpass-human-velocity",
    "total_saved": 3
  }
  ```

### D. User Bookmarks List
- **Endpoint**: `GET /api/user-bookmarks/`
- **Response Format**:
  ```json
  {
    "status": "success",
    "count": 3,
    "saved_slugs": ["slug-1", "slug-2", "slug-3"]
  }
  ```

### E. Trending Topics Radar
- **Endpoint**: `GET /api/trends/`
- **Query Parameters**:
  - `category` (string, optional): Filter by category slug.
  - `limit` (integer, optional): Max records (default: 20).
- **Response Format**:
  ```json
  {
    "status": "success",
    "count": 8,
    "trends": [
      {
        "id": 1,
        "title": "Autonomous AI Agents",
        "slug": "autonomous-ai-agents",
        "category_name": "Technology & Computing",
        "category_slug": "technology",
        "category_color": "#8b5cf6",
        "category_badge": "badge-purple",
        "volume_mentions": 48920,
        "velocity_percentage": 342,
        "sentiment": "bullish",
        "trend_direction": "hot",
        "movement_text": "+18 ranks today",
        "article_count": 124,
        "is_hot": true,
        "calculated_score": 96.8,
        "sparkline": [30, 45, 60, 75, 90, 98, 100],
        "summary": "Enterprise adoption of multi-agent cognitive architectures..."
      }
    ]
  }
  ```

### F. AI News Summarizer (Powered by Groq LLM)
- **Endpoint**: `POST /api/summarize/`
- **Request Body (JSON)**:
  ```json
  {
    "text": "Full article text...",
    "url": "https://example.com/article",
    "format": "short"
  }
  ```
- **Response Format**:
  ```json
  {
    "status": "success",
    "format": "short",
    "format_label": "Short Executive Summary",
    "saved_percentage": 68,
    "words_original": 240,
    "words_summary": 75,
    "summary": "<strong>Executive Synthesis: ...</strong><br><br>• Key point 1...",
    "raw_summary": "Plain text summary...",
    "estimated_read_time": "1 min read"
  }
  ```

### G. TrendBot Chatbot Query (Powered by RAG Pipeline)
- **Endpoint**: `POST /api/chat/`
- **Request Body (JSON)**:
  ```json
  {
    "message": "What are today's top technology trends?",
    "history": []
  }
  ```
- **Response Format**:
  ```json
  {
    "status": "success",
    "reply": "Here are today's highest-velocity technology intelligence trends:<br><br><strong>1. Autonomous AI Agents</strong>...",
    "raw_reply": "Plain text answer...",
    "citations": [
      {
        "id": 1,
        "title": "Autonomous Multi-Agent Networks Surpass Human Engineering Velocity",
        "slug": "autonomous-multi-agent-networks-surpass-human-velocity",
        "source_name": "MIT Technology Review",
        "url": "https://intel.trendora.io/dispatches/autonomous-multi-agent-networks",
        "similarity_score": 0.892,
        "impact_score": 98
      }
    ],
    "suggestions": [
      "Deep-dive into Autonomous AI Agents",
      "Summarize semiconductor fab progress",
      "What are the top business headlines?"
    ],
    "context_count": 2
  }
  ```

### H. Direct RAG Retrieval & Question Answering
- **Endpoint**: `POST /api/rag/`
- **Request Body (JSON)**:
  ```json
  {
    "query": "Quantum error correction milestones",
    "top_k": 3
  }
  ```
- **Response Format**:
  ```json
  {
    "status": "success",
    "answer": "Grounded synthesis citing retrieved articles...",
    "citations": [...],
    "context_count": 3,
    "query": "Quantum error correction milestones"
  }
  ```

### I. Sentiment Analysis
- **Endpoint**: `POST /api/sentiment/`
- **Request Body (JSON)**:
  ```json
  {
    "article_id": 1
  }
  ```
- **Response Format**:
  ```json
  {
    "status": "success",
    "article_id": 1,
    "article_title": "Autonomous Multi-Agent Networks...",
    "sentiment": "BULLISH",
    "confidence": 0.94,
    "explanation": "Detected technological milestone and efficiency indicators.",
    "disclaimer": "Analytical Disclaimer: Sentiment classification reflects reporting tone..."
  }
  ```

### J. AI Thematic Trend Intelligence
- **Endpoint**: `GET /api/trends/intelligence/?topic=autonomous-ai-agents`
- **Response Format**:
  ```json
  {
    "status": "success",
    "topic_title": "Autonomous AI Agents",
    "topic_slug": "autonomous-ai-agents",
    "thematic_explanation": "Accelerating development driven by...",
    "key_entities": ["Autonomous Agents", "Consortia"],
    "observed_evidence": "Tracked across 4 verified dispatches with +340% velocity.",
    "forward_horizon": "Expected transition to volume commercial deployment...",
    "risk_factors": "Manufacturing bottlenecks and regulatory standards.",
    "supporting_articles": [...]
  }
  ```

### K. FAISS Vector Re-indexing
- **Endpoint**: `POST /api/faiss/reindex/`
- **Response Format**:
  ```json
  {
    "status": "success",
    "message": "FAISS index rebuilt with 17 documents.",
    "total_indexed": 17
  }
  ```

### L. Simulated Signal Influx
- **Endpoint**: `GET /api/simulate-signal/`
- **Response Format**:
  ```json
  {
    "status": "success",
    "signal": {
      "title": "Frontier Photonic Interconnect Achieves 1.6 Petabit/s Coherent Bandwidth",
      "category": "technology",
      "source": "MIT Tech Review",
      "impact": 99,
      "velocity": "+420% / 15m",
      "sentiment": "BULLISH"
    },
    "timestamp": "2026-11-20T15:24:00Z"
  }
  ```
