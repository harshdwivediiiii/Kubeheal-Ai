import os
from typing import List, Dict, Any, Optional

from src.models.rag.knowledge_base import KnowledgeBase
from src.models.rag.vector_store import VectorStore
from src.backend.core.config import settings


class RAGSystem:
    def __init__(self):
        self.vector_store = VectorStore()
        self.knowledge_base = KnowledgeBase()
        self._initialize()

    def _initialize(self):
        kb_entries = self.knowledge_base.get_all()
        if kb_entries:
            texts = [
                f"{e.get('title', '')}: {e.get('content', '')}"
                for e in kb_entries
            ]
            metadatas = [
                {"category": e.get("category", ""), "source": e.get("source", "")}
                for e in kb_entries
            ]
            self.vector_store.add_documents(texts, metadatas)

    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        relevant_docs = self.vector_store.search(question, k=k)
        context = "\n\n".join([doc["text"] for doc in relevant_docs])

        return {
            "question": question,
            "context": context,
            "sources": [
                {
                    "text": doc["text"][:200],
                    "metadata": doc["metadata"],
                    "relevance_score": doc["score"],
                }
                for doc in relevant_docs
            ],
            "num_sources": len(relevant_docs),
        }

    def diagnose_failure(self, error_log: str) -> Dict[str, Any]:
        query = f"Kubernetes failure diagnosis: {error_log[:500]}"
        return self.query(query)

    def suggest_remediation(self, issue_type: str) -> Dict[str, Any]:
        query = f"How to fix {issue_type} in Kubernetes"
        return self.query(query)
