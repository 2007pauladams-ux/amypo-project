# TRENDORA — Frontend Routes & Backend API Specifications

This document outlines all frontend user-facing routes, reusable Django template components, and expected backend API endpoints for the **TRENDORA — Real-Time News and Trend Intelligence** platform.

---

## 1. Frontend Web Routes

| Route | View Function | Template | Description |
|---|---|---|---|
| `/` | `views.index` | `templates/intelligence/index.html` | Primary homepage with hero radar, prominent news search bar, breakthrough spotlight story, telemetry cards, and live dispatches feed. |
| `/dashboard/` | `views.dashboard` | `templates/intelligence/dashboard.html` | Comprehensive analyst dashboard with left command sidebar, KPI metrics, hot trending keywords, recent articles, and domain matrix sections. |
| `/search/` | `views.advanced_search` | `templates/intelligence/search.html` | Advanced intelligence search interface with large search bar, trending query tags, domain/date/source/relevance filters, and interactive card results. |
| `/trending/` | `views.trending_topics_view` | `templates/intelligence/trending.html` | Dedicated Trending Topics page spanning Technology, Business, Politics, Sports, Science, Entertainment with momentum meters, sparklines, and signal counts. |
| `/summarizer/` | `views.ai_summarizer_view` | `templates/intelligence/summarizer.html` | AI News Summarizer interface accepting article URL or raw text with Short, Detailed, and Key Points formats, loading states, and clipboard copy. |
| `/ask-ai/` | `views.ask_ai_view` | `templates/intelligence/ask_ai.html` | TrendBot interactive conversational AI assistant with preset inquiries, typing indicators, live chat bubbles, and auto-scroll. |
| `/login/` | `views.login_view` | `templates/auth/login.html` | Secure terminal login with CSRF protection, password visibility toggle, error handling, and demo account credentials. |
| `/register/` | `views.register_view` | `templates/auth/register.html` | New analyst registration page with validation, password confirmation, and automatic profile creation. |
| `/logout/` | `views.logout_view` | *Redirects to `/`* | Closes user session and redirects to homepage with feedback toast. |
| `/forgot-password/` | `views.forgot_password_view` | `templates/auth/forgot_password.html` | Password recovery interface for requesting encrypted reset tokens. |
| `/profile/` | `views.user_profile_view` | `templates/intelligence/profile.html` | Analyst profile management, editable username/email/bio, domain preference checkboxes, and activity counters. |
| `/saved/` | `views.saved_news_view` | `templates/intelligence/saved_news.html` | Dedicated saved intelligence library displaying user bookmarks with one-click remove and clear actions. |

---

## 2. Reusable Django Template Components

Located in `templates/components/`:

### A. Regular News Card
- **File**: `templates/components/news_card.html`
- **Usage**:
  ```django
  {% include 'components/news_card.html' with article=article %}
  ```
- **Features**: Visual thumbnail banner with gradient & geometric pattern, category tag, impact score badge, headline, source wire dot, publication date, summary, sentiment pill, reading time, "Read Article" drawer trigger, and bookmark toggle.

### B. Featured Breakthrough Card
- **File**: `templates/components/news_card_featured.html`
- **Usage**:
  ```django
  {% include 'components/news_card_featured.html' with article=featured_article %}
  ```
- **Features**: Dual-column layout, animated rotating radar scan, dynamic Impact Score Gauge (`1-100`), Trend Velocity badge (`+540% / 1h`), executive synthesis bullet points, and drawer report launcher.

### C. Compact News Card
- **File**: `templates/components/news_card_compact.html`
- **Usage**:
  ```django
  {% include 'components/news_card_compact.html' with article=article %}
  ```
- **Features**: Dense horizontal strip for dashboards and sidebar widgets, showing domain pill, relative timestamp, headline, source name, and impact star.

---

## 3. Backend API Endpoints

### A. Articles Stream Query
- **Endpoint**: `GET /api/articles/`
- **Query Parameters**:
  - `q` (string, optional): Search keyword query matching title, summary, content, source, or category.
  - `category` (string, optional): Category slug (e.g. `technology`, `business`, `politics`, `sports`, `science`, `entertainment`).
  - `topic` (string, optional): Trending topic slug.
  - `sentiment` (string, optional): Sentiment filter (`BULLISH`, `BEARISH`, `HIGH IMPACT`, `DEVELOPING`, `NEUTRAL`).
  - `sort` (string, optional): `latest` (default), `impact`, `velocity`.
- **Response Format**:
  ```json
  {
    "status": "success",
    "count": 8,
    "articles": [
      {
        "id": 1,
        "title": "Next-Gen Neuromorphic AI Processors Achieve 100x Energy Efficiency Milestone",
        "slug": "neuromorphic-ai-processors-100x-energy-efficiency",
        "category_id": 1,
        "category_name": "Technology",
        "category_slug": "technology",
        "category_color": "#8b5cf6",
        "category_badge": "badge-purple",
        "source_name": "MIT Technology Review",
        "source_domain": "technologyreview.com",
        "published_at": "2026-11-20T08:14:00Z",
        "formatted_date": "Nov 20, 2026",
        "time_ago": "14m ago",
        "summary": "Monolithic 3D neuromorphic silicon architecture...",
        "content": "Full multi-paragraph report text...",
        "takeaways": [
          "100x reduction in watt-per-operation envelope.",
          "Zero static leakage power."
        ],
        "read_time_minutes": 5,
        "impact_score": 98,
        "velocity_score": "+540% / 1h",
        "sentiment": "BULLISH",
        "image_gradient": "linear-gradient(135deg, #1e1b4b 0%, #3b0764 100%)",
        "hero_pattern": "neural-grid",
        "is_featured": true,
        "is_breaking": true,
        "views_count": 8420,
        "bookmarks_count": 612
      }
    ]
  }
  ```

---

### B. Single Article Intelligence Report
- **Endpoint**: `GET /api/articles/<slug>/`
- **Description**: Retrieves full intelligence dossier, increments view counter, and adds to user reading history if authenticated.
- **Response Format**:
  ```json
  {
    "status": "success",
    "article": { ... }
  }
  ```

---

### C. Bookmark Toggle
- **Endpoint**: `GET /api/bookmark/<slug>/` or `POST /api/bookmark/<slug>/`
- **Description**: Toggles bookmark in user's `UserProfile.saved_articles` and returns current status.
- **Response Format**:
  ```json
  {
    "status": "success",
    "slug": "neuromorphic-ai-processors-100x-energy-efficiency",
    "bookmarked": true
  }
  ```

---

### D. AI News Summarizer
- **Endpoint**: `POST /api/summarize/`
- **Request Body (JSON or Form-Data)**:
  ```json
  {
    "text": "Full dispatch text content...",
    "url": "https://source.com/article (optional)",
    "format": "short" | "detailed" | "keypoints"
  }
  ```
- **Response Format**:
  ```json
  {
    "status": "success",
    "format": "short",
    "format_label": "Short Executive Briefing",
    "summary": "Synthesized summary content...",
    "bullets": ["Bullet 1", "Bullet 2"],
    "words_original": 240,
    "words_summary": 42,
    "saved_percentage": 82
  }
  ```

---

### E. TrendBot Conversational Chat
- **Endpoint**: `POST /api/chat/`
- **Request Body (JSON or Form-Data)**:
  ```json
  {
    "message": "What are today's top technology trends?"
  }
  ```
- **Response Format**:
  ```json
  {
    "status": "success",
    "reply": "<p>Formatted HTML response with verified dispatches and trends...</p>",
    "timestamp": "14:35:10 UTC"
  }
  ```

---

### F. Real-Time Signal Influx Simulator
- **Endpoint**: `GET /api/simulate-signal/`
- **Description**: Synthesizes and saves a new incoming breaking intelligence signal to SQLite and returns it for live prepend animation.
- **Response Format**:
  ```json
  {
    "status": "success",
    "signal": { ... }
  }
  ```

---

## 4. Test Credentials

- **Demo Username**: `demo_analyst`
- **Password**: `Trendora2026!`
- **Role**: Staff Analyst
