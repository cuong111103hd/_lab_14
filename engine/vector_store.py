import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

class QdrantStore:
    def __init__(self, collection_name: str = "legal_docs"):
        self.collection_name = collection_name
        self.url = os.getenv("QDRANT_URL", ":memory:")
        self.db_path = os.getenv("QDRANT_PATH", "data/qdrant_db")
        if self.url == ":memory:" and not os.getenv("QDRANT_URL"):
            # If no URL is provided, use a local path instead of :memory: for persistence
            self.client = QdrantClient(path=self.db_path)
        elif self.url == ":memory:":
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=self.url)
        self.vector_size = int(os.getenv("QDRANT_VECTOR_SIZE", 1536))
        
        # Initialize collection if it doesn't exist
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        points = []
        for i, chunk in enumerate(chunks):
            points.append(
                models.PointStruct(
                    id=chunk["id"],
                    vector=embeddings[i],
                    payload={
                        "content": chunk["content"],
                        "metadata": chunk["metadata"],
                        "doc_id": chunk.get("doc_id", "unknown")
                    }
                )
            )
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector: List[float], query_text: str = None, limit: int = 5) -> List[Dict]:
        # Using query_points for newer qdrant-client versions
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        )
        results = response.points
        
        formatted_results = []
        for res in results:
            formatted_results.append({
                "id": res.id,
                "score": res.score,
                "content": res.payload.get("content"),
                "metadata": res.payload.get("metadata", {}),
                "doc_id": res.payload.get("doc_id")
            })
        return formatted_results

    def clear(self):
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()
