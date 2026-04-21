import asyncio
import os
import sys
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from engine.retrieval_engine import LegalRetrievalEngine
from dotenv import load_dotenv

load_dotenv()

class MainAgent:
    def __init__(self, model: str = "gpt-4o-mini", config: Dict[str, Any] = None):
        self.model = model
        self.config = config or {
            "system_prompt": "Bạn là một trợ lý pháp luật chuyên nghiệp. Hãy trả lời câu hỏi dựa trên văn bản được cung cấp.",
            "top_k": 3
        }
        self.name = f"LegalSupportAgent-{model}"
        self.retriever = LegalRetrievalEngine()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def query(self, question: str) -> Dict[str, Any]:
        """
        RAG workflow:
        1. Retrieval: Search for relevant legal context.
        2. Generation: Call LLM to generate answer based on context.
        """
        # 1. Retrieval
        retrieved_results = self.retriever.retrieve(question, limit=self.config.get("top_k", 3))
        contexts = [res["content"] for res in retrieved_results]
        retrieved_ids = [res["id"] for res in retrieved_results]
        
        # 2. Preparation
        context_str = "\n---\n".join(contexts)
        prompt = f"""{self.config.get("system_prompt", "Bạn là trợ lý pháp luật.")}

CÂU HỎI: {question}

CÁC ĐOẠN TRÍCH LỤC:
{context_str}

CÂU TRẢ LỜI:"""

        # 3. Generation (Async call via run_in_executor or just regular if using sync client)
        # Using sync client with run_in_executor for async safety in a loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
        )
        
        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return {
            "answer": answer,
            "contexts": contexts,
            "retrieved_ids": retrieved_ids,
            "metadata": {
                "model": self.model,
                "tokens_used": tokens_used,
                "sources": [res["metadata"].get("title", "Unknown Source") for res in retrieved_results]
            }
        }

if __name__ == "__main__":
    agent = MainAgent()
    async def test():
        # Note: You need documents indexed first for this to work
        resp = await agent.query("Quy định về thời gian nghỉ ngơi của người lao động?")
        print(resp["answer"])
    asyncio.run(test())
