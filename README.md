# TRENDORA — Real-Time News and Trend Intelligence

**TRENDORA** is a modular, high-performance technology dashboard and intelligence platform built with **Python 3.13**, **Django 6.1**, **HTML5**, **CSS3**, and **Vanilla JavaScript** (strictly zero React or external JavaScript frameworks).

It synthesizes real-time news dispatches, macroeconomic trends, and frontier technology breakthroughs into a unified command dashboard featuring a dark navy and purple neon aesthetic, Bloomberg Terminal-grade typography, algorithmic trend detection, an AI news summarizer, and TrendBot conversational intelligence powered by **Groq LLMs**, **Sentence Transformers**, and a **FAISS vector database** in a complete **Retrieval-Augmented Generation (RAG)** pipeline.

---

## Architecture Overview

The system is organized into a modular Django architecture with four decoupled applications:

```
TRENDORA/
├── accounts/                  # Authentication, analyst sessions & preference tracking
│   ├── models.py              # UserProfile with preferred categories & bio
│   ├── views.py               # Login, Register, Logout, Forgot Password, Profile views
│   └── urls.py                # Authentication endpoints
│
├── news/                      # News aggregation, normalization & storage
│   ├── models.py              # NewsCategory, NewsSource, NewsArticle, SavedArticle, SearchHistory
│   ├── services/
│   │   └── newsapi_service.py # NewsAPI ingestion, normalization & duplicate prevention
│   ├── management/commands/
│   │   ├── collect_news.py    # Autonomous collection pipeline
│   │   └── seed_trendora.py   # Complete multi-domain initial database seeder
│   ├── views.py               # Index, Dashboard, Advanced Search, Saved News & REST APIs
│   └── urls.py                # News routes & REST endpoints
│
├── trends/                    # Algorithmic trend detection & velocity scoring
│   ├── models.py              # TrendingTopic with calculated scores & sparklines
│   ├── services/
│   │   └── trend_detector.py  # Frequency + recency decay trend detection engine
│   ├── management/commands/
│   │   └── detect_trends.py   # Algorithmic trend detection runner
│   ├── views.py               # Trending Topics view & /api/trends/ endpoint
│   └── urls.py                # Trends routing
│
├── ai/                        # AI Intelligence, RAG Pipeline & Groq LLM Suite
│   ├── services/
│   │   ├── groq_service.py              # Configurable Groq LLM client (Llama 3.3 70B)
│   │   ├── embedding_service.py         # Sentence Transformers (all-MiniLM-L6-v2)
│   │   ├── vector_store.py              # FAISS vector database (IndexFlatIP)
│   │   ├── rag_service.py               # Grounded RAG pipeline with citations
│   │   ├── summarizer_service.py        # Multi-format summarization (Short, Detailed, Keypoints)
│   │   ├── trendbot_service.py          # TrendBot conversational intelligence
│   │   ├── trend_intelligence_service.py# AI-assisted thematic trend analysis
│   │   └── sentiment_service.py         # Objective sentiment analysis (Bullish, Bearish, etc.)
│   ├── management/commands/
│   │   ├── reindex_faiss.py             # Command to vectorize & index DB articles into FAISS
│   │   └── analyze_sentiment.py         # Command to analyze sentiment across articles
│   ├── views.py                         # AI Summarizer, Chat, RAG, Sentiment & FAISS APIs
│   └── urls.py                          # AI routing
│
├── static/
│   ├── css/trendora.css       # Unified design system stylesheet
│   └── js/trendora.js         # Pure vanilla JavaScript client engine
│
├── templates/
│   ├── base.html              # Base shell with live status bar & ticker
│   ├── auth/                  # Login, Register, Forgot Password
│   ├── components/            # Reusable news cards (Featured, Regular, Compact)
│   └── intelligence/          # Index, Dashboard, Search, Trending, Summarizer, Ask AI, Profile, Saved
│
├── data/faiss/                # FAISS vector index binary and metadata mappings
├── trendora_project/          # Root project settings & master URL routing
└── manage.py
```

---

## AI Architecture & RAG Pipeline (Items 21–30)

TRENDORA integrates an enterprise-grade artificial intelligence engine:

```
User Query / Article Text
          │
          ▼
┌──────────────────────────────────────────────┐
│       EmbeddingService (SentenceTransformer) │
│       Model: all-MiniLM-L6-v2 (384 dims)     │
└──────────────────────────────────────────────┘
          │
          ▼ Normalized Unit Vector
┌──────────────────────────────────────────────┐
│       FaissVectorStore (FAISS IndexFlatIP)   │
│       Cosine Similarity Vector Search        │
│       Top-K Article Retrieval & ID Mapping   │
└──────────────────────────────────────────────┘
          │
          ▼ Relevant NewsArticle Objects + Metadata
┌──────────────────────────────────────────────┐
│       Anti-Hallucination Guardrails          │
│       (If similarity < threshold:            │
│        inform user, do NOT invent facts)     │
└──────────────────────────────────────────────┘
          │
          ▼ Grounded Context + Strict Citation Instructions
┌──────────────────────────────────────────────┐
│       GroqService (Groq API)                 │
│       Model: llama-3.3-70b-versatile         │
│       Temperature: 0.2 (Factual & Objective) │
└──────────────────────────────────────────────┘
          │
          ▼
Grounded Answer + Verifiable Citations (Title, Source, Canonical URL)
```

### 1. Groq LLM Integration (Items 21, 22)
- Reusable `GroqService` supporting configurable models (`settings.GROQ_MODEL`, default: `llama-3.3-70b-versatile`).
- Configurable temperature (`GROQ_TEMPERATURE=0.2`), token limits (`GROQ_MAX_TOKENS=2048`), system prompts, and structured output.
- Automatic fallback mechanism ensuring offline unit tests and disconnected sessions never crash.

### 2. Multi-Format News Summarization (Item 23)
- `AiSummarizerService` generates 3 grounded formats strictly based on supplied article text:
  - **Short Executive Summary**: 2-3 concise bullets and strategic horizon takeaway.
  - **Detailed Strategic Briefing**: 4 structured sections (Context & Core Catalyst, Direct Operational Impact, Macroeconomic Horizon, Risk & Velocity).
  - **Actionable Key Points**: 4-6 distinct numbered strategic takeaways.
- Calculates original and summary word counts, percentage reading time saved, and compression ratio.

### 3. Semantic Embeddings & FAISS Vector Database (Items 24, 25)
- Uses `SentenceTransformer` (`all-MiniLM-L6-v2`) generating 384-dimensional dense vectors.
- Vectors are L2-normalized so inner product search in FAISS (`IndexFlatIP`) equals exact cosine similarity.
- Robust handling of empty text, whitespace, and document deduplication.
- Bidirectional row-to-Django-article ID mapping persisted to disk in `data/faiss/`.

### 4. RAG Pipeline & Anti-Hallucination Guardrails (Item 26)
- Converts user questions into query embeddings and retrieves top-k most relevant articles from FAISS.
- If relevant context is absent or below threshold, the system explicitly returns a factual notification stating verified dispatches are unavailable.
- Formats context and requires the LLM to cite specific article titles, publication wires, and URLs.

### 5. TrendBot Chatbot (Item 27)
- Interactive conversational AI assistant in `/ask-ai/` connected to `POST /api/chat/`.
- Answers user inquiries using the RAG pipeline, providing live inline source citations and dynamic suggestions.

### 6. AI-Assisted Trend Intelligence (Item 28)
- `TrendIntelligenceService` analyzes trending topics and supporting articles.
- Identifies recurring entities (institutions, technologies, protocols).
- Explicitly separates **Observed Empirical Evidence** (article frequency and velocity) from **Forward Predictive Claims**.

### 7. Objective Sentiment Analysis (Item 29)
- `SentimentAnalysisService` classifies articles into `BULLISH`, `BEARISH`, `HIGH IMPACT`, or `NEUTRAL`.
- Returns confidence score (0.0 to 1.0) and a 1-2 sentence explanation citing specific keywords from the text.
- Includes platform disclaimer: *"Sentiment reflects reporting framing within evaluated dispatches, not empirical proof or financial certainty."*

---

## Quick Start & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- pip

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory (copied from `.env.example`):
```ini
SECRET_KEY=trendora-production-insecure-key-2026-sec-grade-quantum
DEBUG=True
ALLOWED_HOSTS=*

# News Ingestion Settings
NEWSAPI_KEY=your_newsapi_org_key_here
DEFAULT_COUNTRY=us
COLLECTION_INTERVAL_HOURS=2
DEFAULT_PAGE_SIZE=12

# Groq LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.2
GROQ_MAX_TOKENS=2048

# Embedding & Vector Database Configuration
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
```

### 4. Database Setup & Vector Indexing
```powershell
python manage.py makemigrations accounts news trends ai
python manage.py migrate
python manage.py seed_trendora
python manage.py reindex_faiss
```

### 5. Run the Development Server
```powershell
python manage.py runserver
```
Navigate to: **`http://127.0.0.1:8000/`**

---

## Default Analyst Credentials

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Lead Analyst (Superuser)** | `demo_analyst` | `Trendora2026!` | `analyst@trendora.intel` |

---

## Management Commands

### 1. Vectorize Articles into FAISS (`reindex_faiss`)
```powershell
python manage.py reindex_faiss
```

### 2. Classify Article Sentiment (`analyze_sentiment`)
```powershell
python manage.py analyze_sentiment --limit 20
```

### 3. Automated News Ingestion (`collect_news`)
```powershell
python manage.py collect_news --limit 20
python manage.py collect_news --category technology --limit 15
python manage.py collect_news --query "quantum computing" --everything --limit 10
```

### 4. Algorithmic Trend Detection (`detect_trends`)
```powershell
python manage.py detect_trends --days 7 --min-count 1
```

### 5. Database Seeder (`seed_trendora`)
```powershell
python manage.py seed_trendora
```

---

## Automated Test Suite

A comprehensive test suite of **35 automated unit and integration tests** validates the entire system:

```powershell
python manage.py test
```

### Test Coverage Breakdown:
- `accounts.tests` (7 tests): Registration, password validation, authentication, profile updates, and signals.
- `news.tests` (8 tests): Unique URL constraints, NewsAPI normalization, deduplication, search filtering, and REST endpoints.
- `trends.tests` (4 tests): Trend detection engine, recency decay calculations, views, and `/api/trends/`.
- `ai.tests` (16 tests):
  - Groq client configuration, system prompts, and fallbacks.
  - Sentence Transformers embedding generation (384 dimensions, L2-normalization, empty text handling).
  - FAISS vector database adding, searching, saving, loading, and ORM rebuilding.
  - RAG pipeline retrieval, context compilation, citations, and anti-hallucination guardrails.
  - Multi-format summarization (Short, Detailed, Key Points).
  - TrendBot conversational interaction and dynamic suggestions.
  - AI-assisted trend intelligence and entity extraction.
  - Sentiment analysis classification, confidence, explanation, and model updating.
  - All AI REST endpoints (`/api/summarize/`, `/api/chat/`, `/api/rag/`, `/api/sentiment/`, `/api/trends/intelligence/`, `/api/faiss/reindex/`).

---

## REST & AJAX API Catalog

| Method | Endpoint | Description | Sample Query / Body |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/summarize/` | AI article text/URL summarization | `{"text": "...", "format": "short"}` |
| `POST` | `/api/chat/` | TrendBot RAG chatbot query | `{"message": "What are today's top tech trends?"}` |
| `POST` | `/api/rag/` | Direct RAG semantic retrieval & answer | `{"query": "quantum error correction", "top_k": 3}` |
| `POST` | `/api/sentiment/` | Sentiment analysis of article or text | `{"article_id": 1}` |
| `GET` | `/api/trends/intelligence/`| AI thematic trend analysis & entities | `?topic=autonomous-ai-agents` |
| `POST` | `/api/faiss/reindex/` | Triggers re-indexing of DB into FAISS | Rebuilds dense vector index |
| `GET` | `/api/articles/` | Paginated article retrieval with filters | `?q=quantum&category=technology&sort=impact` |
| `GET` | `/api/articles/<slug>/` | Full article payload for reader modal | `/api/articles/autonomous-multi-agent-networks/`|
| `POST` | `/api/bookmark/<slug>/` | Toggle article bookmark for user | Bookmark toggle |
| `GET` | `/api/user-bookmarks/` | Slugs saved by current analyst | Syncs client badge |
| `GET` | `/api/trends/` | Ranked trending topics | `?category=all&limit=20` |
| `GET` | `/api/simulate-signal/` | Influx simulation dispatch | Live telemetry push |
