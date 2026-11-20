import os
import json
import logging
from pathlib import Path
import numpy as np
import faiss
from django.conf import settings

from .embedding_service import EmbeddingService, EMBEDDING_DIM

logger = logging.getLogger('trendora.faiss')

class FaissVectorStore:
    """
    FAISS-powered vector database manager for TRENDORA.
    Indexes article embeddings using cosine similarity (IndexFlatIP),
    maintains persistent row-to-article mappings, and executes semantic retrieval.
    """

    def __init__(self, index_path=None, metadata_path=None, dimension=EMBEDDING_DIM):
        self.dimension = dimension
        self.storage_dir = getattr(settings, 'FAISS_STORAGE_DIR', Path(settings.BASE_DIR) / 'data' / 'faiss')
        self.index_path = Path(index_path or getattr(settings, 'FAISS_INDEX_PATH', self.storage_dir / 'articles_index.faiss'))
        self.metadata_path = Path(metadata_path or getattr(settings, 'FAISS_METADATA_PATH', self.storage_dir / 'articles_metadata.json'))
        
        self.embedding_service = EmbeddingService()
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Mappings
        self.id_to_article_id = []          # index_row -> article_id
        self.article_id_to_row = {}          # article_id -> index_row
        self.metadata_store = {}             # str(article_id) -> metadata dict
        
        # Load existing index if present
        self.load()

    def count(self):
        """Returns total number of indexed vectors."""
        return self.index.ntotal if self.index else 0

    def add_documents(self, article_ids, texts, metadata_list=None):
        """
        Embeds and adds multiple documents to the FAISS index.
        Deduplicates against existing article IDs.
        """
        if not article_ids or not texts:
            return 0

        metadata_list = metadata_list or [{}] * len(article_ids)
        
        # Filter duplicates or already-indexed documents
        new_ids = []
        new_texts = []
        new_meta = []
        
        for aid, txt, meta in zip(article_ids, texts, metadata_list):
            if aid in self.article_id_to_row:
                # Document already in index; update its metadata
                self.metadata_store[str(aid)] = meta
                continue
            new_ids.append(aid)
            new_texts.append(txt)
            new_meta.append(meta)

        if not new_ids:
            return 0

        # Generate vectors
        embeddings = self.embedding_service.get_embeddings(new_texts)
        if embeddings.shape[0] == 0:
            return 0

        start_row = self.index.ntotal
        self.index.add(embeddings)

        for i, (aid, meta) in enumerate(zip(new_ids, new_meta)):
            row = start_row + i
            self.id_to_article_id.append(aid)
            self.article_id_to_row[aid] = row
            self.metadata_store[str(aid)] = meta

        self.save()
        logger.info(f"Added {len(new_ids)} documents to FAISS index. Total index count: {self.count()}.")
        return len(new_ids)

    def update_document(self, article_id, text, metadata=None):
        """
        Updates an existing document in the vector store.
        If already present, updates metadata; full vector update triggers rebuild if needed.
        """
        if article_id not in self.article_id_to_row:
            return self.add_documents([article_id], [text], [metadata or {}])
        
        if metadata:
            self.metadata_store[str(article_id)] = metadata
            self.save()
        return 1

    def search(self, query, top_k=5, score_threshold=0.0):
        """
        Performs semantic similarity search against indexed news articles.
        Query can be a string query or a pre-computed numpy vector.
        Returns list of tuples: (article_id, score, metadata)
        """
        if self.count() == 0:
            logger.warning("FAISS search called on empty index.")
            return []

        if isinstance(query, str):
            query_vector = self.embedding_service.get_embedding(query)
        elif isinstance(query, np.ndarray):
            query_vector = query.astype(np.float32)
        else:
            return []

        if len(query_vector.shape) == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        # Normalize query vector if needed
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm

        k = min(top_k, self.count())
        scores, indices = self.index.search(query_vector, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.id_to_article_id):
                continue
            if score < score_threshold:
                continue

            article_id = self.id_to_article_id[idx]
            meta = self.metadata_store.get(str(article_id), {})
            results.append((article_id, float(score), meta))

        return results

    def save(self):
        """Persists the FAISS index binary and metadata mapping to disk."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path))

            data = {
                'id_to_article_id': self.id_to_article_id,
                'metadata_store': self.metadata_store,
            }
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"FAISS index saved to {self.index_path} with {self.count()} entries.")
            return True
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            return False

    def load(self):
        """Reloads FAISS index binary and metadata mapping from disk."""
        if not self.index_path.exists() or not self.metadata_path.exists():
            return False

        try:
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.id_to_article_id = data.get('id_to_article_id', [])
            self.metadata_store = data.get('metadata_store', {})
            self.article_id_to_row = {aid: idx for idx, aid in enumerate(self.id_to_article_id)}

            logger.info(f"Loaded FAISS index with {self.count()} entries from {self.index_path}.")
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.id_to_article_id = []
            self.article_id_to_row = {}
            self.metadata_store = {}
            return False

    def rebuild_index_from_db(self):
        """
        Indexes all NewsArticle records from the Django database into FAISS.
        """
        from news.models import NewsArticle

        articles = list(NewsArticle.objects.all().select_related('category', 'source'))
        if not articles:
            logger.warning("No NewsArticle records found in database to index.")
            return 0

        # Reset in-memory index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_to_article_id = []
        self.article_id_to_row = {}
        self.metadata_store = {}

        article_ids = []
        texts = []
        metadata_list = []

        for a in articles:
            # Build rich semantic representation
            text = f"{a.title}. {a.summary}. {a.content[:1000]}"
            meta = {
                'id': a.id,
                'title': a.title,
                'slug': a.slug,
                'source_name': a.get_source_display(),
                'source_domain': a.get_domain_display(),
                'url': a.url,
                'category_slug': a.category.slug if a.category else 'general',
                'category_name': a.category.name if a.category else 'General',
                'impact_score': a.impact_score,
                'published_at': a.published_at.isoformat(),
            }
            article_ids.append(a.id)
            texts.append(text)
            metadata_list.append(meta)

        return self.add_documents(article_ids, texts, metadata_list)
