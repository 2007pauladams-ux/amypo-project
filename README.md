# TRENDORA — Real-Time News and Trend Intelligence

**TRENDORA** is a professional, high-performance technology dashboard and intelligence platform built with **Django**, **HTML5**, **CSS3**, and **Vanilla JavaScript** (zero frontend frameworks).

It synthesizes real-time technological breakthroughs, macro signals, and trending topics into an executive command interface featuring a dark navy and purple neon aesthetic, Bloomberg Terminal/Linear-grade typography, dynamic live charts, instant search, and deep-dive intelligence reports.

---

## Key Features

1. **Futuristic Dark Navy & Purple Visual Architecture**
   - Color system: Deep space midnight `#05070f`, surface navy `#0e1424`, glowing neon purple `#8b5cf6`, and cyan accents `#06b6d4`.
   - Subtle glowing borders, glassmorphism (`backdrop-filter: blur(16px)`), micro-interactions, and animated radar sweep effects.

2. **TRENDORA Vector Branding & Top Telemetry Bar**
   - High-tech vector logo with dynamic light-sweep animation.
   - Continuous live breaking flash dispatches ticker (pauses on hover).
   - Real-time UTC & Local millisecond clocks updated dynamically.
   - Grid status telemetry: 18ms latency, 48K+ global signals monitored.

3. **Prominent News Search Bar & Instant Filtering**
   - Large glowing search bar with keyboard shortcut (`/` or `Ctrl + K`).
   - Pure vanilla JavaScript client-side instant search across titles, summaries, sources, and categories with search query term highlighting.
   - Category filter pills with live counters.
   - Quick "Clear" button (`X`) when query is present.

4. **Breakthrough Story Spotlight (Hero Section)**
   - Featured breakthrough report with radar scan visual effect.
   - Dynamic **Impact Score Gauge** (e.g. `98/100`) and **Velocity Meter** (`+540% / 1h`).
   - Executive Synthesis Takeaways bullet points.
   - Slide-over intelligence reader trigger.

5. **Trending Topics & Velocity Radar**
   - High-velocity topic clusters with rank badges (`#01`, `#02`, ...).
   - Real-time SVG sparklines displaying momentum curves.
   - Interactive trend filtering: Clicking any trend card filters headlines immediately to that specific topic.

6. **Latest Headlines Stream**
   - Multiple view modes: **Rich Grid View** and **Dense Terminal List View** (persisted to `localStorage`).
   - Multi-attribute sorting: **Latest First**, **Highest Impact Score**, or **Trending Velocity**.
   - Category color dots, sentiment pills (`BULLISH`, `BEARISH`, `HIGH IMPACT`, `DEVELOPING`), reading time, and publication timestamps.

7. **Interactive Deep-Dive Reader Drawer**
   - Slide-over reader drawer with reading progress bar.
   - Complete multi-paragraph intelligence breakdown, key takeaway bullets, source citations, impact scores, and reading time.
   - Share button: Copies direct hash link (`#slug`) to clipboard with animated toast notification.

8. **Saved Intel / Bookmarks Library**
   - Bookmark any dispatch with one click; saved securely in `localStorage`.
   - Live bookmark counter in the navigation bar.
   - Dedicated slide-over drawer to review, inspect, or clear saved reports.

9. **Live Signal Influx Simulator**
   - "SIMULATE SIGNAL" button dynamically decodes incoming intelligence signals from the backend API (`/api/simulate-signal/`) and prepends them with a smooth glowing arrival animation.

10. **100% Responsive Architecture**
    - Optimized for widescreen desktops (1440px+), laptops, tablets, and mobile smartphones.
    - Touch-friendly drawer interactions and mobile drawer navigation.

---

## Technology Stack

- **Backend**: Python 3.13 / Django 6.1
- **Templates**: Django Templates (HTML5, Semantic ARIA)
- **Styling**: Modern CSS3 (Custom properties, CSS Grid, Flexbox, Glassmorphism, Keyframe animations)
- **Client Scripting**: Pure Vanilla JavaScript (ES6+, zero external libraries or frameworks)
- **Database**: SQLite3 (pre-seeded with rich, realistic frontier technology articles and trends)

---

## Running the Application

To launch the TRENDORA development server:

```powershell
python manage.py runserver
```

Then open your browser at:
```
http://127.0.0.1:8000/
```

### Running the Test Suite

```powershell
python manage.py test
```

### Seeding Data (Optional)

```powershell
python manage.py seed_trendora
```

---

## Keyboard Shortcuts

- `/` or `Ctrl + K`: Focus the prominent news search bar
- `Escape`: Close any open drawer (Article Reader or Saved Bookmarks)
