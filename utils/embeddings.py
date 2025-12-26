from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import os

class EmbeddingManager:
    """Manages embedding models and operations"""
    def __init__(self):
        self._model = None
        self.model_name = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.device = os.environ.get("EMBEDDING_DEVICE", "cpu")

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings
        except Exception as e:
            print(f"Failed to generate embeddings: {e}")
            raise

    def embed_text(self, text: str) -> np.ndarray:
        return self.embed_texts([text])[0]

    def get_embedding_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

embedding_manager = EmbeddingManager()
