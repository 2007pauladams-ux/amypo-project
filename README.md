# TRENDORA — Real-Time News and Trend Intelligence

**TRENDORA** is a modular, high-performance technology dashboard and intelligence platform built with **Python 3.13**, **Django 6.1**, **HTML5**, **CSS3**, and **Vanilla JavaScript** (strictly zero React or external JavaScript frameworks).

It synthesizes real-time news dispatches, macroeconomic trends, and frontier technology breakthroughs into a unified command dashboard featuring a dark navy and purple neon aesthetic, Bloomberg Terminal-grade typography, algorithmic trend detection, an AI news summarizer, and TrendBot conversational intelligence.

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
├── ai/                        # AI intelligence suite
│   ├── services/
│   │   ├── summarizer_service.py # Multi-format summarization (Short, Detailed, Keypoints)
│   │   └── trendbot_service.py   # TrendBot contextual intelligence chatbot
│   ├── views.py               # AI Summarizer & TrendBot views + REST endpoints
│   └── urls.py                # AI routing
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
├── trendora_project/          # Root project settings & master URL routing
└── manage.py
```

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
NEWSAPI_KEY=your_newsapi_org_key_here
DEFAULT_COUNTRY=us
COLLECTION_INTERVAL_HOURS=2
DEFAULT_PAGE_SIZE=12
```

> **Note**: Even if `NEWSAPI_KEY` is not provided or quota-limited, TRENDORA includes a built-in synthetic signal generator ensuring full offline development, testing, and continuous operation without external API dependencies.

### 4. Database Setup & Migrations
```powershell
python manage.py makemigrations accounts news trends ai
python manage.py migrate
```

### 5. Seed Initial Intelligence Data
Populate the database with foundational categories, sources, trending topics, baseline news articles, and a demo analyst user account:
```powershell
python manage.py seed_trendora
```

### 6. Run the Development Server
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

### 1. Automated News Ingestion (`collect_news`)
Fetches news from NewsAPI, normalizes payloads, extracts sources/categories, generates key takeaways, and updates or creates database records preventing duplicates based on canonical URL.

```powershell
# Ingest top headlines across all categories
python manage.py collect_news --limit 20

# Ingest specifically for a technology or business category
python manage.py collect_news --category technology --limit 15

# Deep search everything query
python manage.py collect_news --query "quantum computing" --everything --limit 10
```

### 2. Algorithmic Trend Detection (`detect_trends`)
Analyzes collected article titles and summaries, extracts n-grams and entities, applies exponential publication recency decay and impact score weighting, and synchronizes `TrendingTopic` database records with sparklines.

```powershell
# Analyze the last 7 days of articles
python manage.py detect_trends --days 7 --min-count 1
```

### 3. Database Seeder (`seed_trendora`)
```powershell
python manage.py seed_trendora
```

---

## Algorithmic Trend Detection Model

TRENDORA evaluates emerging topics through a dual-scoring model distinguishing **calculated algorithmic trends** from **broadcast mention volume**:

$$\text{Calculated Score} = \left(\sum_{a \in \text{Articles}} \frac{\text{Impact Score}_a}{100 \times (1 + \text{hours ago}_a \times 0.12)}\right) \times (1 + \ln(1 + |\text{Articles}|)) \times 10$$

- **Impact Score**: 1-100 rating based on source tier, content density, and technical terminology.
- **Recency Decay**: Harmonic time decay preventing stale dispatches from dominating the radar.
- **Frequency Multiplier**: Logarithmic dampener preventing runaway amplification.
- **Sparklines**: Dynamically generated 7-point momentum curves.

---

## Automated Test Suite

A comprehensive test suite with 26 automated unit and integration tests covers authentication, models, services, duplicate prevention, views, and JSON REST APIs.

Run tests:
```powershell
python manage.py test
```

Test coverage includes:
- `accounts.tests`: User registration, password validation, authentication, profile updates, and signals.
- `news.tests`: Unique URL constraints, NewsAPI normalization, deduplication, search filtering, and REST endpoints.
- `trends.tests`: Trend detection engine, recency decay calculations, views, and /api/trends/ endpoint.
- `ai.tests`: Summarization service (short, detailed, keypoints), TrendBot contextual responses, and REST endpoints.

---

## REST & AJAX API Catalog

| Method | Endpoint | Description | Sample Query / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/articles/` | Paginated article retrieval | `?q=quantum&category=technology&sort=impact&page=1` |
| `GET` | `/api/articles/<slug>/` | Full article payload for reader modal | `/api/articles/superconducting-qubit-array/` |
| `POST` | `/api/bookmark/<slug>/` | Toggle article bookmark for user | `/api/bookmark/autonomous-ai-agents/` |
| `GET` | `/api/user-bookmarks/` | Slugs saved by current analyst | Synchronizes nav bookmark badge |
| `GET` | `/api/trends/` | Ranked trending topics | `?category=all&limit=20` |
| `POST` | `/api/summarize/` | AI article text/URL summarization | `{"text": "...", "format": "short"}` |
| `POST` | `/api/chat/` | Interactive TrendBot query | `{"message": "What are today's top tech trends?"}` |
| `GET` | `/api/simulate-signal/` | Influx simulation dispatch | Live telemetry push trigger |

---

## Frontend Design & Navigation Standards

- **Theme**: Dark navy (`#05070f`, `#0e1424`), purple neon (`#8b5cf6`), and cyan accents (`#06b6d4`).
- **Typography**: Inter (UI prose) and JetBrains Mono (metrics, telemetry, timestamps).
- **Frontend Stack**: Strictly vanilla JavaScript (no React, Vue, or client build tools).
- **Accessibility**: Full keyboard shortcuts (`/` for search, `Esc` for reader drawer), ARIA attributes, and high-contrast color tags.
