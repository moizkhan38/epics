import pytest
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def embedding_service():
    """Create an embedding service instance"""
    return EmbeddingService()


def test_generate_embedding(embedding_service):
    """Test generating a single embedding"""
    text = "This is a test project for building a SaaS application"
    embedding = embedding_service.generate_embedding(text)

    assert isinstance(embedding, list)
    assert len(embedding) == 384  # Default dimension for all-MiniLM-L6-v2
    assert all(isinstance(x, float) for x in embedding)


def test_generate_embeddings_batch(embedding_service):
    """Test generating multiple embeddings"""
    texts = [
        "Project management tool",
        "E-commerce platform",
        "Social media application"
    ]
    embeddings = embedding_service.generate_embeddings_batch(texts)

    assert isinstance(embeddings, list)
    assert len(embeddings) == len(texts)
    assert all(len(emb) == 384 for emb in embeddings)


def test_compute_similarity(embedding_service):
    """Test computing similarity between embeddings"""
    text1 = "Build a project management tool"
    text2 = "Create a task tracking application"
    text3 = "Design a recipe sharing website"

    emb1 = embedding_service.generate_embedding(text1)
    emb2 = embedding_service.generate_embedding(text2)
    emb3 = embedding_service.generate_embedding(text3)

    # Similar texts should have higher similarity
    similarity_related = embedding_service.compute_similarity(emb1, emb2)
    similarity_unrelated = embedding_service.compute_similarity(emb1, emb3)

    assert 0 <= similarity_related <= 1
    assert 0 <= similarity_unrelated <= 1
    assert similarity_related > similarity_unrelated
