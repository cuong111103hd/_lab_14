import os
from typing import List, Dict
from engine.vector_store import QdrantStore
from engine.embedder import OpenAIEmbedder
from dotenv import load_dotenv

load_dotenv()

class LegalRetrievalEngine:
    def __init__(self):
        self.store = QdrantStore()
        self.embedder = OpenAIEmbedder()

    def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        # 1. Embedding query
        query_vector = self.embedder.embed_query(query)

        # 2. Search in Qdrant
        results = self.store.search(query_vector, query, limit=limit)
        
        return results

    def index_documents(self, documents: List[Dict]):
        """
        Expects a list of dicts: {"metadata": {...}, "content": "..."}
        """
        all_chunks = []
        from agent.chunker import MarkdownLegalChunker
        chunker = MarkdownLegalChunker()
        
        for doc in documents:
            chunks = chunker.chunk_document(doc["metadata"], doc["content"])
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return
            
        # Embed in batches
        texts = [c["content"] for c in all_chunks]
        embeddings = self.embedder.embed_batch(texts)
        
        # Upsert to Qdrant
        self.store.upsert_chunks(all_chunks, embeddings)
        print(f"Indexed {len(all_chunks)} chunks.")
