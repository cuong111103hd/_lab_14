import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIEmbedder:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is missing in .env")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.vector_size = int(os.getenv("QDRANT_VECTOR_SIZE", 1536)) # text-embedding-3-small default dim is 1536

    def embed_text(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.vector_size if self.model == "text-embedding-3-small" or self.model == "text-embedding-3-large" else None
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"OpenAI Embedder Error: {e}")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.vector_size if self.model == "text-embedding-3-small" or self.model == "text-embedding-3-large" else None
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise RuntimeError(f"OpenAI Embedder Error for batch: {e}")

    def embed_query(self, text: str) -> list[float]:
        return self.embed_text(text)
