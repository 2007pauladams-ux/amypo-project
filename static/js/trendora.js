/**
 * TRENDORA — Real-Time News and Trend Intelligence
 * Vanilla JavaScript Core Engine (No Frameworks)
 * Handles: Live Telemetry, Instant Search, Reader Drawer, Bookmarks,
 * Dashboard Tabs, Advanced Search, Trending Radar, AI Summarizer, TrendBot Chat.
 */

(function () {
  'use strict';

  // Global State
  const state = {
    articles: [],
    categories: [],
    trendingTopics: [],
    activeCategory: 'all',
    activeTopic: null,
    searchQuery: '',
    sortMode: 'latest',
    viewMode: localStorage.getItem('trendora_view') || 'grid',
    bookmarks: JSON.parse(localStorage.getItem('trendora_bookmarks') || '[]'),
    activeArticleSlug: null,
    summarizerFormat: 'short'
  };

  // Cached DOM Elements
  const elements = {
    articlesGrid: document.getElementById('articlesStreamGrid'),
    resultsCount: document.getElementById('feedResultsCount'),
    activeFilterName: document.getElementById('activeFilterName'),
    searchInput: document.getElementById('mainSearchInput'),
    clearSearchBtn: document.getElementById('clearSearchBtn'),
    searchSubmitBtn: document.getElementById('searchSubmitBtn'),
    categoryPills: document.querySelectorAll('.cat-pill'),
    sortSelect: document.getElementById('sortSelect'),
    viewGridBtn: document.getElementById('viewGridBtn'),
    viewListBtn: document.getElementById('viewListBtn'),
    liveClockUtc: document.getElementById('liveClockUtc'),
    liveClockLocal: document.getElementById('liveClockLocal'),
    simulateSignalBtn: document.getElementById('simulateSignalBtn'),
    bookmarkNavTrigger: document.getElementById('bookmarkNavTrigger'),
    bookmarkBadge: document.getElementById('navBookmarkBadge'),
    
    // Drawers & Modals
    drawerBackdrop: document.getElementById('drawerBackdrop'),
    readerDrawer: document.getElementById('readerDrawer'),
    readerCloseBtn: document.getElementById('readerCloseBtn'),
    drawerReadingProgress: document.getElementById('drawerReadingProgress'),
    drawerScrollContainer: document.getElementById('drawerScrollContainer'),
    readerCategory: document.getElementById('readerCategory'),
    readerSentiment: document.getElementById('readerSentiment'),
    readerTitle: document.getElementById('readerTitle'),
    readerSource: document.getElementById('readerSource'),
    readerTime: document.getElementById('readerTime'),
    readerImpact: document.getElementById('readerImpact'),
    readerVelocity: document.getElementById('readerVelocity'),
    readerTakeawaysList: document.getElementById('readerTakeawaysList'),
    readerBodyContent: document.getElementById('readerBodyContent'),
    readerBookmarkBtn: document.getElementById('readerBookmarkBtn'),
    readerShareBtn: document.getElementById('readerShareBtn'),

    // Bookmarks Drawer
    bookmarksDrawer: document.getElementById('bookmarksDrawer'),
    bookmarksCloseBtn: document.getElementById('bookmarksCloseBtn'),
    bookmarksList: document.getElementById('bookmarksList'),
    clearBookmarksBtn: document.getElementById('clearBookmarksBtn'),

    // Mobile Menu
    mobileMenuBtn: document.getElementById('mobileMenuBtn'),
    navMenu: document.getElementById('navMenu'),

    // Toasts
    toastContainer: document.getElementById('toastContainer')
  };

  // Main Initialize Entry Point
  function init() {
    loadInitialData();
    setupLiveClocks();
    setupGlobalEventListeners();
    setupKeyboardShortcuts();
    updateBookmarkBadge();
    applyViewMode(state.viewMode);
    
    // Page Specific Modules
    if (elements.articlesGrid && document.getElementById('articlesJsonData')) {
      renderArticles();
    }
    initDashboard();
    initAdvancedSearch();
    initTrendingPage();
    initSummarizer();
    initTrendBot();
    initAuthHelpers();
    initSavedNewsPage();
  }

  // Load Initial JSON Data rendered by Django
  function loadInitialData() {
    try {
      const articlesDataEl = document.getElementById('articlesJsonData');
      if (articlesDataEl && articlesDataEl.textContent) {
        state.articles = JSON.parse(articlesDataEl.textContent);
      }
      const categoriesDataEl = document.getElementById('categoriesJsonData');
      if (categoriesDataEl && categoriesDataEl.textContent) {
        state.categories = JSON.parse(categoriesDataEl.textContent);
      }
      const trendingDataEl = document.getElementById('trendingJsonData');
      if (trendingDataEl && trendingDataEl.textContent) {
        state.trendingTopics = JSON.parse(trendingDataEl.textContent);
      }
    } catch (err) {
      console.warn("Could not parse embedded JSON data:", err);
    }
  }

  // Live Clocks Engine (UTC & Local)
  function setupLiveClocks() {
    function updateClock() {
      const now = new Date();
      if (elements.liveClockUtc) {
        const utcHours = String(now.getUTCHours()).padStart(2, '0');
        const utcMins = String(now.getUTCMinutes()).padStart(2, '0');
        const utcSecs = String(now.getUTCSeconds()).padStart(2, '0');
        elements.liveClockUtc.textContent = `${utcHours}:${utcMins}:${utcSecs} UTC`;
      }
      if (elements.liveClockLocal) {
        const hours = String(now.getHours()).padStart(2, '0');
        const mins = String(now.getMinutes()).padStart(2, '0');
        const secs = String(now.getSeconds()).padStart(2, '0');
        elements.liveClockLocal.textContent = `${hours}:${mins}:${secs}`;
      }
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // Toast Notification System
  function showToast(message, type = 'normal') {
    if (!elements.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'success' ? 'toast-success' : type === 'alert' ? 'toast-alert' : ''}`;
    
    let iconSvg = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
      </svg>
    `;

    if (type === 'success') {
      iconSvg = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      `;
    }

    toast.innerHTML = `
      ${iconSvg}
      <span>${escapeHTML(message)}</span>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }

  // Setup Global Listeners
  function setupGlobalEventListeners() {
    // Search input on homepage
    let debounceTimer;
    if (elements.searchInput) {
      elements.searchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value.trim().toLowerCase();
        toggleClearSearchBtn();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          if (elements.articlesGrid) renderArticles();
        }, 150);
      });
    }

    if (elements.clearSearchBtn) {
      elements.clearSearchBtn.addEventListener('click', () => {
        if (elements.searchInput) elements.searchInput.value = '';
        state.searchQuery = '';
        toggleClearSearchBtn();
        if (elements.articlesGrid) renderArticles();
        elements.searchInput.focus();
      });
    }

    // Category Filter Pills on Homepage
    elements.categoryPills.forEach((pill) => {
      pill.addEventListener('click', () => {
        const catSlug = pill.getAttribute('data-category');
        elements.categoryPills.forEach((p) => p.classList.remove('active'));
        pill.classList.add('active');
        state.activeCategory = catSlug;
        state.activeTopic = null;
        if (elements.articlesGrid) renderArticles();
      });
    });

    // Sort Dropdown on Homepage
    if (elements.sortSelect) {
      elements.sortSelect.addEventListener('change', (e) => {
        state.sortMode = e.target.value;
        if (elements.articlesGrid) renderArticles();
      });
    }

    // View Mode Toggle (Grid vs List)
    if (elements.viewGridBtn && elements.viewListBtn) {
      elements.viewGridBtn.addEventListener('click', () => applyViewMode('grid'));
      elements.viewListBtn.addEventListener('click', () => applyViewMode('list'));
    }

    // Simulation Trigger Button
    if (elements.simulateSignalBtn) {
      elements.simulateSignalBtn.addEventListener('click', triggerSimulatedSignal);
    }

    // Reader & Bookmarks Close Triggers
    if (elements.readerCloseBtn) elements.readerCloseBtn.addEventListener('click', closeAllDrawers);
    if (elements.bookmarksCloseBtn) elements.bookmarksCloseBtn.addEventListener('click', closeAllDrawers);
    if (elements.drawerBackdrop) elements.drawerBackdrop.addEventListener('click', closeAllDrawers);
    if (elements.clearBookmarksBtn) elements.clearBookmarksBtn.addEventListener('click', clearAllBookmarks);

    // Mobile Hamburger
    if (elements.mobileMenuBtn && elements.navMenu) {
      elements.mobileMenuBtn.addEventListener('click', () => {
        elements.navMenu.classList.toggle('mobile-open');
      });
    }

    // Global Delegated Click Handling (Open Reader, Bookmark, Share)
    document.addEventListener('click', (e) => {
      // Open Article Reader
      const readTrigger = e.target.closest('[data-open-article]');
      if (readTrigger) {
        e.preventDefault();
        const slug = readTrigger.getAttribute('data-open-article');
        openArticleReader(slug);
        return;
      }

      // Bookmark Toggle
      const bookmarkTrigger = e.target.closest('[data-bookmark-slug]');
      if (bookmarkTrigger) {
        e.preventDefault();
        e.stopPropagation();
        const slug = bookmarkTrigger.getAttribute('data-bookmark-slug');
        toggleBookmark(slug, bookmarkTrigger);
        return;
      }

      // Share Action
      const shareTrigger = e.target.closest('[data-share-slug]');
      if (shareTrigger) {
        e.preventDefault();
        e.stopPropagation();
        const slug = shareTrigger.getAttribute('data-share-slug');
        const url = `${window.location.origin}/#${slug}`;
        navigator.clipboard.writeText(url).then(() => {
          showToast('Intelligence dispatch link copied to clipboard', 'success');
        });
        return;
      }
    });

    // Check URL hash on page load
    if (window.location.hash) {
      const slug = window.location.hash.replace('#', '');
      if (slug && !slug.includes('Section') && !slug.includes('panel')) {
        setTimeout(() => openArticleReader(slug), 350);
      }
    }
  }

  // Keyboard Shortcuts Engine
  function setupKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      // "/" or "Ctrl+K" to focus search
      if ((e.key === '/' || (e.ctrlKey && e.key.toLowerCase() === 'k')) && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        const targetSearch = document.getElementById('advancedSearchInput') || elements.searchInput;
        if (targetSearch) {
          targetSearch.focus();
          targetSearch.select();
        }
      }

      // "Escape" to close drawers
      if (e.key === 'Escape') {
        closeAllDrawers();
      }
    });
  }

  // Toggle Clear Search Button
  function toggleClearSearchBtn() {
    if (!elements.clearSearchBtn) return;
    elements.clearSearchBtn.style.display = state.searchQuery.length > 0 ? 'inline-flex' : 'none';
  }

  // Apply View Mode
  function applyViewMode(mode) {
    state.viewMode = mode;
    localStorage.setItem('trendora_view', mode);

    const grids = document.querySelectorAll('.articles-stream-grid');
    grids.forEach(g => {
      if (mode === 'list') g.classList.add('list-view');
      else g.classList.remove('list-view');
    });

    if (elements.viewGridBtn && elements.viewListBtn) {
      elements.viewGridBtn.classList.toggle('active', mode === 'grid');
      elements.viewListBtn.classList.toggle('active', mode === 'list');
    }
  }

  // Render Homepage Articles
  function renderArticles() {
    if (!elements.articlesGrid) return;
    const filtered = getFilteredArticles();

    if (elements.resultsCount) elements.resultsCount.textContent = filtered.length;
    if (elements.activeFilterName) {
      let label = 'All Streams';
      if (state.activeCategory !== 'all') {
        const cat = state.categories.find(c => c.slug === state.activeCategory);
        label = cat ? cat.name : state.activeCategory;
      }
      if (state.searchQuery) label += ` / "${state.searchQuery}"`;
      elements.activeFilterName.textContent = label;
    }

    if (filtered.length === 0) {
      elements.articlesGrid.innerHTML = `
        <div class="empty-results-state">
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
          <h3 class="empty-title">No Intelligence Signals Found</h3>
          <p class="empty-sub">No verified dispatches matched your current search filters.</p>
        </div>
      `;
      return;
    }

    elements.articlesGrid.innerHTML = filtered.map(a => renderCardHtml(a)).join('');
  }

  function getFilteredArticles() {
    let result = [...state.articles];
    if (state.activeCategory && state.activeCategory !== 'all') {
      result = result.filter(a => a.category_slug === state.activeCategory);
    }
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase();
      result = result.filter(a => 
        (a.title && a.title.toLowerCase().includes(q)) ||
        (a.summary && a.summary.toLowerCase().includes(q)) ||
        (a.source_name && a.source_name.toLowerCase().includes(q)) ||
        (a.category_name && a.category_name.toLowerCase().includes(q))
      );
    }
    if (state.sortMode === 'impact') {
      result.sort((a, b) => b.impact_score - a.impact_score);
    } else if (state.sortMode === 'velocity') {
      result.sort((a, b) => b.views_count - a.views_count);
    } else {
      result.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
    }
    return result;
  }

  function renderCardHtml(article) {
    const isBookmarked = state.bookmarks.includes(article.slug);
    const sentimentClass = `sentiment-${article.sentiment.toLowerCase().replace(/\s+/g, '-')}`;

    return `
      <article class="article-intel-card" id="article-card-${article.slug}">
        <div class="card-thumb-banner" style="background: ${article.image_gradient};">
          <div class="card-thumb-pattern ${article.hero_pattern}"></div>
          <div class="card-thumb-overlay">
            <span class="cat-pill ${article.category_badge || 'badge-purple'}">${escapeHTML(article.category_name)}</span>
            <span class="card-thumb-impact">IMPACT ${article.impact_score}/100</span>
          </div>
        </div>
        <div class="card-body-content">
          <div class="article-card-header">
            <div class="article-source-row">
              <span class="source-dot" style="background: ${article.category_color || '#8b5cf6'}"></span>
              <span>${escapeHTML(article.source_name)}</span>
            </div>
            <span class="article-date-stamp">${escapeHTML(article.formatted_date || article.time_ago)}</span>
          </div>
          <h3 class="article-card-title" data-open-article="${article.slug}">
            ${highlightText(article.title, state.searchQuery)}
          </h3>
          <p class="article-card-summary">
            ${highlightText(article.summary, state.searchQuery)}
          </p>
          <div class="article-card-meta">
            <span class="sentiment-pill ${sentimentClass}">${escapeHTML(article.sentiment)}</span>
            <span>•</span>
            <span>${escapeHTML(article.time_ago || 'recent')}</span>
            <span>•</span>
            <span>${article.read_time_minutes} min read</span>
          </div>
          <div class="article-card-actions">
            <button class="read-intel-btn" data-open-article="${article.slug}">
              Read Article
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
            <div class="quick-action-btns">
              <button class="icon-action-btn ${isBookmarked ? 'bookmarked' : ''}" data-bookmark-slug="${article.slug}" title="Bookmark Article">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="${isBookmarked ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
              </button>
              <button class="icon-action-btn" data-share-slug="${article.slug}" title="Share Article">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="18" cy="5" r="3"></circle>
                  <circle cx="6" cy="12" r="3"></circle>
                  <circle cx="18" cy="19" r="3"></circle>
                  <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                  <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </article>
    `;
  }

  // Open Article Reader Drawer
  async function openArticleReader(slug) {
    let article = state.articles.find(a => a.slug === slug);
    if (!article) {
      try {
        const res = await fetch(`/api/articles/${slug}/`);
        const data = await res.json();
        if (data.status === 'success') article = data.article;
      } catch (e) {
        console.error("Could not fetch article detail:", e);
      }
    }
    if (!article) return;

    state.activeArticleSlug = slug;
    window.location.hash = slug;

    if (elements.readerCategory) {
      elements.readerCategory.textContent = article.category_name;
      elements.readerCategory.className = `cat-pill ${article.category_badge || 'badge-purple'}`;
    }
    if (elements.readerSentiment) {
      elements.readerSentiment.textContent = article.sentiment;
      elements.readerSentiment.className = `sentiment-pill sentiment-${article.sentiment.toLowerCase().replace(/\s+/g, '-')}`;
    }
    if (elements.readerTitle) elements.readerTitle.textContent = article.title;
    if (elements.readerSource) elements.readerSource.textContent = `${article.source_name} (${article.source_domain})`;
    if (elements.readerTime) elements.readerTime.textContent = `${article.time_ago || 'recent'} • ${article.read_time_minutes} min read`;
    if (elements.readerImpact) elements.readerImpact.textContent = `${article.impact_score}/100`;
    if (elements.readerVelocity) elements.readerVelocity.textContent = article.velocity_score || '+280% / 1h';

    if (elements.readerTakeawaysList) {
      const takeaways = article.takeaways || [];
      elements.readerTakeawaysList.innerHTML = takeaways.map(t => `<li class="takeaway-bullet">${escapeHTML(t)}</li>`).join('');
    }

    if (elements.readerBodyContent) {
      const paragraphs = article.content.split('\n\n').filter(Boolean);
      elements.readerBodyContent.innerHTML = paragraphs.map(p => `<p>${escapeHTML(p)}</p>`).join('');
    }

    updateReaderBookmarkState();

    if (elements.drawerScrollContainer) elements.drawerScrollContainer.scrollTop = 0;
    if (elements.drawerReadingProgress) elements.drawerReadingProgress.style.width = '0%';

    elements.drawerBackdrop.classList.add('active');
    elements.readerDrawer.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function updateReaderBookmarkState() {
    if (!elements.readerBookmarkBtn || !state.activeArticleSlug) return;
    const isBookmarked = state.bookmarks.includes(state.activeArticleSlug);
    elements.readerBookmarkBtn.classList.toggle('bookmarked', isBookmarked);
    elements.readerBookmarkBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="${isBookmarked ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
      </svg>
      <span>${isBookmarked ? 'Saved to Intel' : 'Bookmark Intel'}</span>
    `;
  }

  // Toggle Bookmark Handler
  async function toggleBookmark(slug, btnElement) {
    const index = state.bookmarks.indexOf(slug);
    let bookmarked = false;
    if (index > -1) {
      state.bookmarks.splice(index, 1);
      bookmarked = false;
      showToast('Article removed from saved intelligence');
    } else {
      state.bookmarks.push(slug);
      bookmarked = true;
      showToast('Article saved to intelligence library', 'success');
    }
    localStorage.setItem('trendora_bookmarks', JSON.stringify(state.bookmarks));
    updateBookmarkBadge();

    // Sync with backend API
    try {
      fetch(`/api/bookmark/${slug}/`);
    } catch (e) {}

    // Update active button state
    if (btnElement) {
      btnElement.classList.toggle('bookmarked', bookmarked);
      const svg = btnElement.querySelector('svg');
      if (svg) svg.setAttribute('fill', bookmarked ? 'currentColor' : 'none');
    }

    // If on Saved News page and unbookmarking, smoothly remove card
    const savedCard = document.getElementById(`article-card-${slug}`) || document.getElementById(`compact-card-${slug}`);
    if (window.location.pathname.includes('/saved/') && !bookmarked && savedCard) {
      savedCard.style.opacity = '0';
      savedCard.style.transform = 'scale(0.95)';
      savedCard.style.transition = 'all 0.3s ease';
      setTimeout(() => {
        savedCard.remove();
        const countEl = document.getElementById('savedPageTotalCount');
        if (countEl) countEl.textContent = state.bookmarks.length;
      }, 300);
    }

    if (elements.articlesGrid && document.getElementById('articlesJsonData')) renderArticles();
    if (elements.bookmarksDrawer && elements.bookmarksDrawer.classList.contains('active')) renderBookmarksList();
  }

  function updateBookmarkBadge() {
    if (elements.bookmarkBadge) {
      elements.bookmarkBadge.textContent = state.bookmarks.length;
    }
  }

  function renderBookmarksList() {
    if (!elements.bookmarksList) return;
    const saved = state.articles.filter(a => state.bookmarks.includes(a.slug));
    if (saved.length === 0) {
      elements.bookmarksList.innerHTML = `
        <div class="empty-results-state" style="padding: 2.5rem 1rem;">
          <h4 style="font-size: 1.1rem; margin-bottom: 0.4rem; color: #fff;">No Saved Intelligence</h4>
          <p style="font-size: 0.85rem; color: var(--text-muted);">Bookmark any article across the streams to view here.</p>
        </div>
      `;
      return;
    }
    elements.bookmarksList.innerHTML = saved.map(a => `
      <div class="bookmark-item-card">
        <div style="display: flex; justify-content: space-between; font-size: 0.72rem;">
          <span style="color: ${a.category_color}; font-weight: 600;">${escapeHTML(a.category_name)}</span>
          <span style="color: var(--text-muted); font-family: var(--font-mono);">${escapeHTML(a.time_ago || '')}</span>
        </div>
        <h4 class="bookmark-item-title" data-open-article="${a.slug}">${escapeHTML(a.title)}</h4>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.4rem;">
          <span style="font-size: 0.72rem; color: var(--text-secondary);">${escapeHTML(a.source_name)}</span>
          <button class="icon-action-btn bookmarked" data-bookmark-slug="${a.slug}" title="Remove Bookmark">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
          </button>
        </div>
      </div>
    `).join('');
  }

  function clearAllBookmarks() {
    if (state.bookmarks.length === 0) return;
    if (confirm('Clear all saved intelligence dispatches?')) {
      state.bookmarks = [];
      localStorage.removeItem('trendora_bookmarks');
      updateBookmarkBadge();
      renderBookmarksList();
      showToast('All saved bookmarks cleared');
    }
  }

  function closeAllDrawers() {
    if (elements.drawerBackdrop) elements.drawerBackdrop.classList.remove('active');
    if (elements.readerDrawer) elements.readerDrawer.classList.remove('active');
    if (elements.bookmarksDrawer) elements.bookmarksDrawer.classList.remove('active');
    document.body.style.overflow = '';
    state.activeArticleSlug = null;
    history.replaceState(null, null, ' ');
  }

  // Simulation Trigger
  async function triggerSimulatedSignal() {
    try {
      showToast('Connecting to global satellite feeds...');
      const res = await fetch('/api/simulate-signal/');
      const data = await res.json();
      if (data.status === 'success' && data.signal) {
        state.articles.unshift(data.signal);
        if (elements.articlesGrid) {
          renderArticles();
          setTimeout(() => {
            const card = document.getElementById(`article-card-${data.signal.slug}`);
            if (card) {
              card.classList.add('new-arrival');
              card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }, 100);
        }
        showToast(`⚡ New Signal Decoded: ${data.signal.title.substring(0, 42)}...`, 'success');
      }
    } catch (e) {
      showToast('Failed to receive simulated signal', 'alert');
    }
  }

  // ============================================================================
  // MODULE: DASHBOARD INTERACTIONS
  // ============================================================================
  function initDashboard() {
    const tabs = document.querySelectorAll('.cat-matrix-tab');
    if (tabs.length === 0) return;

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const target = tab.getAttribute('data-target-tab');
        const panels = document.querySelectorAll('.category-panel-block');

        panels.forEach(p => {
          if (target === 'all-cats' || p.id === `panel-${target}`) {
            p.style.display = 'block';
          } else {
            p.style.display = 'none';
          }
        });
      });
    });

    // Populate mini saved list in dashboard
    const dashSaved = document.getElementById('dashSavedMiniList');
    if (dashSaved) {
      if (state.bookmarks.length === 0) {
        dashSaved.innerHTML = '<p style="font-size: 0.8rem; color: var(--text-muted); padding: 0.5rem 0;">No bookmarked dispatches currently stored.</p>';
      } else {
        dashSaved.innerHTML = `
          <div style="font-size: 0.85rem; color: var(--purple-light); font-weight: 600; padding: 0.5rem 0;">
            ${state.bookmarks.length} dispatches saved in your library.
          </div>
          <a href="/saved/" class="btn-dash-action" style="font-size: 0.78rem; padding: 0.4rem 0.8rem; width: 100%; justify-content: center;">
            Open Stored Archive →
          </a>
        `;
      }
    }
  }

  // ============================================================================
  // MODULE: ADVANCED SEARCH PAGE
  // ============================================================================
  function initAdvancedSearch() {
    const advInput = document.getElementById('advancedSearchInput');
    const catSelect = document.getElementById('filterCategory');
    const dateSelect = document.getElementById('filterDate');
    const srcSelect = document.getElementById('filterSource');
    const sortSelect = document.getElementById('filterSort');
    const resetBtn = document.getElementById('advResetFiltersBtn');
    const clearBtn = document.getElementById('advClearBtn');
    const suggestTags = document.querySelectorAll('.suggest-tag-btn');
    const resultsGrid = document.getElementById('advResultsGrid');
    const resultsCountEl = document.getElementById('advResultsCount');

    if (!advInput || !resultsGrid) return;

    // Load initial embedded data for search
    let advArticles = [];
    const jsonEl = document.getElementById('advArticlesJson');
    if (jsonEl && jsonEl.textContent) {
      try { advArticles = JSON.parse(jsonEl.textContent); } catch (e) {}
    }

    function runFilter() {
      const q = advInput.value.trim().toLowerCase();
      const cat = catSelect ? catSelect.value : 'all';
      const date = dateSelect ? dateSelect.value : 'all';
      const src = srcSelect ? srcSelect.value : 'all';
      const sort = sortSelect ? sortSelect.value : 'relevance';

      if (clearBtn) clearBtn.style.display = q.length > 0 ? 'inline-flex' : 'none';

      let filtered = [...advArticles];

      if (q) {
        filtered = filtered.filter(a => 
          (a.title && a.title.toLowerCase().includes(q)) ||
          (a.summary && a.summary.toLowerCase().includes(q)) ||
          (a.source_name && a.source_name.toLowerCase().includes(q)) ||
          (a.category_name && a.category_name.toLowerCase().includes(q))
        );
      }

      if (cat !== 'all') {
        filtered = filtered.filter(a => a.category_slug === cat);
      }

      if (src !== 'all') {
        filtered = filtered.filter(a => a.source_name.toLowerCase() === src.toLowerCase());
      }

      if (sort === 'latest') {
        filtered.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
      } else if (sort === 'velocity') {
        filtered.sort((a, b) => b.views_count - a.views_count);
      } else {
        filtered.sort((a, b) => b.impact_score - a.impact_score);
      }

      if (resultsCountEl) resultsCountEl.textContent = filtered.length;

      if (filtered.length === 0) {
        resultsGrid.innerHTML = `
          <div class="empty-results-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              <line x1="8" y1="11" x2="14" y2="11"></line>
            </svg>
            <h3 class="empty-title">No Matching Intelligence Signals</h3>
            <p class="empty-sub">Try broadening your search term or selecting All Domains.</p>
          </div>
        `;
      } else {
        resultsGrid.innerHTML = filtered.map(a => renderCardHtml(a)).join('');
      }
    }

    let timer;
    advInput.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(runFilter, 150);
    });

    if (catSelect) catSelect.addEventListener('change', runFilter);
    if (dateSelect) dateSelect.addEventListener('change', runFilter);
    if (srcSelect) srcSelect.addEventListener('change', runFilter);
    if (sortSelect) sortSelect.addEventListener('change', runFilter);

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        advInput.value = '';
        clearBtn.style.display = 'none';
        runFilter();
        advInput.focus();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        advInput.value = '';
        if (catSelect) catSelect.value = 'all';
        if (dateSelect) dateSelect.value = 'all';
        if (srcSelect) srcSelect.value = 'all';
        if (sortSelect) sortSelect.value = 'relevance';
        if (clearBtn) clearBtn.style.display = 'none';
        runFilter();
        showToast('Search parameters reset');
      });
    }

    suggestTags.forEach(btn => {
      btn.addEventListener('click', () => {
        advInput.value = btn.getAttribute('data-query');
        runFilter();
      });
    });
  }

  // ============================================================================
  // MODULE: TRENDING TOPICS PAGE
  // ============================================================================
  function initTrendingPage() {
    const domainBtns = document.querySelectorAll('.domain-tab-btn');
    const cards = document.querySelectorAll('.trending-master-card');
    if (domainBtns.length === 0 || cards.length === 0) return;

    domainBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        domainBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const domain = btn.getAttribute('data-domain');

        cards.forEach(card => {
          if (domain === 'all' || card.getAttribute('data-domain') === domain) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  // ============================================================================
  // MODULE: AI NEWS SUMMARIZER
  // ============================================================================
  function initSummarizer() {
    const textInput = document.getElementById('articleTextInput');
    const urlInput = document.getElementById('articleUrlInput');
    const formatBtns = document.querySelectorAll('.format-option-btn');
    const submitBtn = document.getElementById('btnSummarizeSubmit');
    const loadSampleBtn = document.getElementById('btnLoadSample');
    const clearBtn = document.getElementById('btnClearInput');
    const copyBtn = document.getElementById('btnCopySummary');
    const charCount = document.getElementById('charCountText');
    const loading = document.getElementById('summarizerLoading');
    const placeholder = document.getElementById('summarizerPlaceholder');
    const resultBox = document.getElementById('summarizerResult');
    const resultText = document.getElementById('resultTextBody');
    const formatBadge = document.getElementById('resultFormatBadge');
    const compressionMetric = document.getElementById('compressionMetric');
    const outputWordCount = document.getElementById('outputWordCount');
    const outputTools = document.getElementById('outputTools');

    if (!submitBtn || !resultBox) return;

    // Word counter
    if (textInput && charCount) {
      textInput.addEventListener('input', () => {
        const words = textInput.value.trim().split(/\s+/).filter(Boolean).length;
        charCount.textContent = `${words} words`;
      });
    }

    // Format selection
    formatBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        formatBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.summarizerFormat = btn.getAttribute('data-format');
      });
    });

    // Sample Loader
    if (loadSampleBtn) {
      loadSampleBtn.addEventListener('click', () => {
        textInput.value = `A landmark publication released today by an international consortium of university laboratories and semiconductor fabricators details a working 3D neuromorphic core that mimics mammalian cortical sparse-coding. Operating on event-driven asynchronous spikes rather than clock-synchronous tensor matrix arithmetic, the processor demonstrated an astonishing 100-fold reduction in energy draw during live robotic spatial navigation and acoustic signal filtering tasks. The breakthrough relies on atomic-layer-deposited memristive crossbar arrays directly bonded onto sub-2nm FinFET logic layers. Unlike conventional GPUs that consume hundreds of watts during continuous token generation, neuromorphic cores only expend power when an informative spike registers across synaptic nodes. Industry implications are immediate: drone avionics, wearable biomedical monitors, and planetary exploration probes can now execute contextual reasoning models in real time without bulky cooling systems or reliance on cloud tethering.`;
        if (charCount) {
          const words = textInput.value.trim().split(/\s+/).filter(Boolean).length;
          charCount.textContent = `${words} words`;
        }
        showToast('Sample technology dispatch loaded');
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (textInput) textInput.value = '';
        if (urlInput) urlInput.value = '';
        if (charCount) charCount.textContent = '0 words';
        if (placeholder) placeholder.style.display = 'block';
        if (resultBox) resultBox.style.display = 'none';
        if (outputTools) outputTools.style.display = 'none';
        showToast('Summarizer inputs cleared');
      });
    }

    // Submit handler
    submitBtn.addEventListener('click', async () => {
      const text = textInput ? textInput.value.trim() : '';
      const url = urlInput ? urlInput.value.trim() : '';

      if (!text && !url) {
        showToast('Please provide an article URL or text to summarize', 'alert');
        return;
      }

      placeholder.style.display = 'none';
      resultBox.style.display = 'none';
      loading.style.display = 'block';

      try {
        const response = await fetch('/api/summarize/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, url, format: state.summarizerFormat })
        });
        const data = await response.json();

        loading.style.display = 'none';

        if (data.status === 'success') {
          resultBox.style.display = 'flex';
          if (outputTools) outputTools.style.display = 'block';
          if (formatBadge) formatBadge.textContent = data.format_label;
          if (compressionMetric) compressionMetric.textContent = `Estimated ${data.saved_percentage}% reading time saved`;
          if (outputWordCount) outputWordCount.textContent = `Words: ${data.words_summary} (Original: ${data.words_original})`;
          if (resultText) resultText.innerHTML = data.summary;
          showToast('Intelligence synthesis completed successfully', 'success');
        } else {
          placeholder.style.display = 'block';
          showToast(data.message || 'Synthesis failed', 'alert');
        }
      } catch (err) {
        loading.style.display = 'none';
        placeholder.style.display = 'block';
        showToast('Synthesis network error', 'alert');
      }
    });

    // Copy Summary
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        if (!resultText) return;
        const text = resultText.innerText;
        navigator.clipboard.writeText(text).then(() => {
          showToast('Summary copied to clipboard', 'success');
        });
      });
    }
  }

  // ============================================================================
  // MODULE: TRENDBOT AI CHATBOT
  // ============================================================================
  function initTrendBot() {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const viewport = document.getElementById('chatMessagesViewport');
    const typingIndicator = document.getElementById('typingIndicator');
    const presetBtns = document.querySelectorAll('.chat-preset-btn');
    const clearChatBtn = document.getElementById('btnClearChatHistory');

    if (!chatInput || !viewport) return;

    function appendMessage(sender, text, isBot = false) {
      const row = document.createElement('div');
      row.className = `chat-message-row ${isBot ? 'bot-row' : 'user-row'}`;
      const now = new Date();
      const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      row.innerHTML = `
        <div class="chat-avatar ${isBot ? 'bot-avatar' : 'user-avatar'}">${isBot ? 'TB' : 'YOU'}</div>
        <div class="chat-bubble ${isBot ? 'bot-bubble' : 'user-bubble'}">
          <div class="bubble-header">
            <span class="bubble-sender">${isBot ? 'TrendBot' : 'Analyst'}</span>
            <span class="bubble-timestamp">${timeStr}</span>
          </div>
          <div class="bubble-text">${text}</div>
        </div>
      `;

      viewport.appendChild(row);
      viewport.scrollTop = viewport.scrollHeight;
    }

    async function sendPrompt(promptText) {
      if (!promptText) return;
      appendMessage('Analyst', escapeHTML(promptText), false);
      if (chatInput) chatInput.value = '';

      if (typingIndicator) {
        typingIndicator.style.display = 'flex';
        viewport.scrollTop = viewport.scrollHeight;
      }

      try {
        const res = await fetch('/api/chat/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: promptText })
        });
        const data = await res.json();

        if (typingIndicator) typingIndicator.style.display = 'none';

        if (data.status === 'success') {
          appendMessage('TrendBot', data.reply, true);
        } else {
          appendMessage('TrendBot', 'Encountered an anomaly in signal telemetry buffer.', true);
        }
      } catch (err) {
        if (typingIndicator) typingIndicator.style.display = 'none';
        appendMessage('TrendBot', 'Connection timeout with core intelligence hub.', true);
      }
    }

    if (chatForm) {
      chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        sendPrompt(msg);
      });
    }

    if (chatInput) {
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          const msg = chatInput.value.trim();
          sendPrompt(msg);
        }
      });
    }

    presetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const prompt = btn.getAttribute('data-prompt');
        sendPrompt(prompt);
      });
    });

    if (clearChatBtn) {
      clearChatBtn.addEventListener('click', () => {
        viewport.innerHTML = `
          <div class="chat-message-row bot-row">
            <div class="chat-avatar bot-avatar">TB</div>
            <div class="chat-bubble bot-bubble">
              <div class="bubble-header">
                <span class="bubble-sender">TrendBot</span>
                <span class="bubble-timestamp">Just now</span>
              </div>
              <div class="bubble-text">
                <p>Chat memory reset. What intelligence signal or trend would you like to explore next?</p>
              </div>
            </div>
          </div>
        `;
        showToast('Chat history cleared');
      });
    }
  }

  // ============================================================================
  // MODULE: AUTHENTICATION HELPERS
  // ============================================================================
  function initAuthHelpers() {
    const toggles = document.querySelectorAll('.password-toggle-btn');
    toggles.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');
        const input = document.getElementById(targetId);
        if (!input) return;

        const eyeOpen = btn.querySelector('.eye-open');
        const eyeClosed = btn.querySelector('.eye-closed');

        if (input.type === 'password') {
          input.type = 'text';
          if (eyeOpen) eyeOpen.style.display = 'none';
          if (eyeClosed) eyeClosed.style.display = 'inline';
        } else {
          input.type = 'password';
          if (eyeOpen) eyeOpen.style.display = 'inline';
          if (eyeClosed) eyeClosed.style.display = 'none';
        }
      });
    });
  }

  // ============================================================================
  // MODULE: SAVED NEWS PAGE
  // ============================================================================
  function initSavedNewsPage() {
    const clearSavedBtn = document.getElementById('btnClearAllSavedPage');
    if (clearSavedBtn) {
      clearSavedBtn.addEventListener('click', () => {
        if (confirm('Permanently clear all saved intelligence reports?')) {
          state.bookmarks = [];
          localStorage.removeItem('trendora_bookmarks');
          updateBookmarkBadge();
          const grid = document.getElementById('savedNewsGrid');
          if (grid) {
            grid.innerHTML = `
              <div class="empty-results-state">
                <h3 class="empty-title">All Saved Intelligence Cleared</h3>
                <p class="empty-sub">Your personal briefing archive has been reset.</p>
              </div>
            `;
          }
          const countEl = document.getElementById('savedPageTotalCount');
          if (countEl) countEl.textContent = '0';
          showToast('Saved intelligence cleared');
        }
      });
    }
  }

  // Utility Helpers
  function highlightText(text, query) {
    if (!query || !text) return escapeHTML(text);
    const escapedText = escapeHTML(text);
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escapedText.replace(regex, '<mark style="background: rgba(168, 85, 247, 0.4); color: #fff; padding: 0 2px; border-radius: 2px;">$1</mark>');
  }

  function escapeHTML(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // DOM Content Loaded Handler
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
