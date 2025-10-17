"""Semantic embeddings using sentence-transformers."""

import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache


class EmbeddingGenerator:
    """Generate semantic embeddings for code."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize embedding model.

        Args:
            model_name: Sentence transformer model name
        """
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> np.ndarray:
        """Generate embedding for text.

        Args:
            text: Code or query text

        Returns:
            Embedding vector as numpy array
        """
        # Convert to numpy and ensure it's a 1D array
        embedding = self.model.encode(text, convert_to_numpy=True)
        return np.asarray(embedding, dtype=np.float32)

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings.

        Args:
            emb1: First embedding
            emb2: Second embedding

        Returns:
            Similarity score [0, 1]
        """
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))
