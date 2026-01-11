from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings for similarity search"""

    def __init__(self):
        """Initialize the embedding model"""
        try:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(
                "embedding_model_loaded",
                model=settings.EMBEDDING_MODEL,
                dimension=settings.EMBEDDING_DIMENSION
            )
        except Exception as e:
            logger.error("failed_to_load_embedding_model", error=str(e))
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a text

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e), text_length=len(text))
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error("batch_embedding_generation_failed", error=str(e), batch_size=len(texts))
            raise

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
