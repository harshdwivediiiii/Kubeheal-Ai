import os
from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer

from src.backend.core.config import settings


class VectorStore:
    def __init__(self, store_type: str = None):
        self.store_type = store_type or settings.vector_store_type
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index = None
        self.documents = []
        self.metadatas = []

    def add_documents(
        self, texts: List[str], metadatas: Optional[List[Dict]] = None
    ):
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        if metadatas is None:
            metadatas = [{} for _ in texts]

        for i, (text, embedding, metadata) in enumerate(
            zip(texts, embeddings, metadatas)
        ):
            self.documents.append({"id": i, "text": text, "metadata": metadata})

        if self.store_type == "faiss":
            self._build_faiss_index(embeddings)
        elif self.store_type == "chroma":
            self._build_chroma_index(texts, embeddings, metadatas)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_model.encode([query])[0]

        if self.store_type == "faiss":
            return self._search_faiss(query_embedding, k)
        elif self.store_type == "chroma":
            return self._search_chroma(query_embedding, k)
        else:
            return self._search_bruteforce(query_embedding, k)

    def _build_faiss_index(self, embeddings):
        import faiss
        import numpy as np

        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(embeddings).astype(np.float32))

    def _build_chroma_index(self, texts, embeddings, metadatas):
        pass

    def _search_faiss(self, query_embedding, k: int):
        import numpy as np

        distances, indices = self.index.search(
            np.array([query_embedding]).astype(np.float32), k
        )
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append({
                    "id": doc["id"],
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": float(1.0 / (1.0 + distances[0][i])),
                })
        return results

    def _search_chroma(self, query_embedding, k: int):
        return self._search_bruteforce(query_embedding, k)

    def _search_bruteforce(self, query_embedding, k: int):
        import numpy as np

        scores = []
        for doc in self.documents:
            doc_emb = self.embedding_model.encode([doc["text"]])[0]
            similarity = np.dot(query_embedding, doc_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)
            )
            scores.append(similarity)

        top_indices = np.argsort(scores)[-k:][::-1]
        return [
            {
                "id": self.documents[i]["id"],
                "text": self.documents[i]["text"],
                "metadata": self.documents[i]["metadata"],
                "score": float(scores[i]),
            }
            for i in top_indices
        ]
