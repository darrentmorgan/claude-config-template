"""Unit tests for semantic embeddings.

Tests Nomic Embed Code integration.
"""

import pytest
from code_graph.retrieval.embeddings import EmbeddingGenerator


class TestEmbeddings:
    """Test embedding generation."""

    @pytest.fixture
    def generator(self):
        """Create embedding generator."""
        # Use small model for testing
        return EmbeddingGenerator(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def test_generate_code_embedding(self, generator):
        """Test generating embedding for code snippet."""
        code = "def greet(name):\n    return f'Hello, {name}'"

        embedding = generator.encode(code)

        # Should return vector
        assert embedding is not None
        assert len(embedding) > 0
        # Check it's a numpy array with numeric values
        import numpy as np
        assert isinstance(embedding, np.ndarray)
        assert embedding.dtype in [np.float32, np.float64, np.float16]

    def test_embedding_similarity(self, generator):
        """Test computing similarity between embeddings."""
        code1 = "def add(a, b): return a + b"
        code2 = "def sum(x, y): return x + y"
        code3 = "def print_hello(): print('hello')"

        emb1 = generator.encode(code1)
        emb2 = generator.encode(code2)
        emb3 = generator.encode(code3)

        # Similar functions should have higher similarity
        sim_12 = generator.cosine_similarity(emb1, emb2)
        sim_13 = generator.cosine_similarity(emb1, emb3)

        assert sim_12 > sim_13  # add/sum more similar than add/print
        assert 0.0 <= sim_12 <= 1.0
