import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Dict, Any
from utils.embeddings import embedding_manager


class VectorStore:
    """FAISS-based vector store for similarity search"""
    def __init__(self):
        self.index = None
        self.documents = []
        self.metadata = []
        self.dimension = None
        self.index_path = os.environ.get("FAISS_INDEX_PATH", "faiss.index")
        self.metadata_path = f"{self.index_path}.metadata"
        dir_path = os.path.dirname(self.index_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        self.load_index()

    def _initialize_index(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)

    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]] = None):
        if not texts:
            return
        try:
            embeddings = embedding_manager.embed_texts(texts)
            if self.index is None:
                self._initialize_index(embeddings.shape[1])
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            self.index.add(embeddings.astype('float32'))
            self.documents.extend(texts)
            if metadata:
                self.metadata.extend(metadata)
            else:
                self.metadata.extend([{"index": len(self.documents) + i} for i in range(len(texts))])
        except Exception as e:
            print(f"Failed to add documents: {e}")
            raise

    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        if self.index is None or self.index.ntotal == 0:
            return []
        try:
            query_embedding = embedding_manager.embed_text(query)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    results.append((self.documents[idx], float(score), self.metadata[idx] if idx < len(self.metadata) else {}))
            return results
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def save_index(self):
        try:
            if self.index is not None:
                faiss.write_index(self.index, self.index_path)
                with open(self.metadata_path, 'wb') as f:
                    pickle.dump({
                        'documents': self.documents,
                        'metadata': self.metadata,
                        'dimension': self.dimension
                    }, f)
        except Exception as e:
            print(f"Failed to save vector store: {e}")

    def load_index(self):
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadata = data['metadata']
                    self.dimension = data['dimension']
        except Exception as e:
            print(f"Could not load existing vector store: {e}")

    def clear(self):
        self.index = None
        self.documents = []
        self.metadata = []
        self.dimension = None
        for path in [self.index_path, self.metadata_path]:
            if os.path.exists(path):
                os.remove(path)

    def get_stats(self) -> Dict[str, Any]:
        # If no metadata, return 0
        if not self.metadata:
            return {
                "total_documents": 0,
                "index_size": self.index.ntotal if self.index else 0,
                "dimension": self.dimension,
                "index_exists": self.index is not None
            }
        # Count unique filenames in metadata as number of documents, fallback to chunk count if no filenames
        filenames = [meta.get("filename") for meta in self.metadata if meta.get("filename")]
        if filenames:
            unique_files = set(filenames)
            total_documents = len(unique_files)
        else:
            total_documents = len(self.documents)
        return {
            "total_documents": total_documents,
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_exists": self.index is not None
        }


# Export the vector_store instance
vector_store = VectorStore()