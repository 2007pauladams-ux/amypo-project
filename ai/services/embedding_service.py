import os
import hashlib
import logging
import numpy as np
from django.conf import settings

logger = logging.getLogger('trendora.embeddings')

EMBEDDING_DIM = 384

class EmbeddingService:
    """
    Semantic text embedding generator for TRENDORA using Sentence Transformers.
    Converts article titles, descriptions, and queries into 384-dimensional
    L2-normalized vectors for FAISS vector search.
    """

    def __init__(self, model_name=None):
        self.model_name = model_name or getattr(settings, 'EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
        self._model = None
        self._dimension = EMBEDDING_DIM

    @property
    def dimension(self):
        return self._dimension

    def _get_model(self):
        """Lazy loader for the SentenceTransformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # Try loading from local cache first (offline friendly)
                try:
                    self._model = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    self._model = SentenceTransformer(self.model_name)
                logger.info(f"SentenceTransformer '{self.model_name}' loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {e}. Using deterministic semantic projection.")
                self._model = False
        return self._model

    def get_embedding(self, text):
        """
        Generates an L2-normalized 384-dimensional float32 vector for a single string.
        Handles empty or whitespace text cleanly.
        """
        if not text or not str(text).strip():
            return np.zeros(self._dimension, dtype=np.float32)

        cleaned_text = " ".join(str(text).split())
        embeddings = self.get_embeddings([cleaned_text])
        return embeddings[0]

    def get_embeddings(self, texts):
        """
        Generates L2-normalized float32 vectors for a batch of strings.
        Shape: (len(texts), 384)
        """
        if not texts:
            return np.empty((0, self._dimension), dtype=np.float32)

        processed = []
        for t in texts:
            if t and str(t).strip():
                processed.append(" ".join(str(t).split()))
            else:
                processed.append("")

        model = self._get_model()

        if model:
            try:
                raw_vectors = model.encode(
                    processed,
                    batch_size=32,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )
                return raw_vectors.astype(np.float32)
            except Exception as e:
                logger.error(f"Error during model.encode: {e}. Falling back to deterministic projection.")

        # Deterministic semantic hash projection (offline resilient)
        vectors = []
        for txt in processed:
            vectors.append(self._fallback_projection(txt))
        return np.vstack(vectors).astype(np.float32)

    def _fallback_projection(self, text):
        """
        Generates a deterministic pseudo-semantic normalized vector via hash n-gram projection.
        Guarantees exact dimension 384 and unit length.
        """
        if not text:
            return np.zeros(self._dimension, dtype=np.float32)

        vec = np.zeros(self._dimension, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
            pos = h % self._dimension
            sign = 1.0 if (h // self._dimension) % 2 == 0 else -1.0
            weight = 1.0 / (1.0 + 0.1 * idx)
            vec[pos] += sign * weight

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
