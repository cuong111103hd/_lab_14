import asyncio
import os
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMJudge:
    def __init__(self, models: List[str] = ["gpt-4o", "gpt-5.4-nano"]):
        self.models = models
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.rubrics = {
            "accuracy": "Chấm điểm từ 1-5 dựa trên độ chính xác so với Ground Truth. 5: Hoàn toàn chính xác, 1: Hoàn toàn sai hoặc bịa đặt.",
            "professionalism": "Chấm điểm từ 1-5 dựa trên sự chuyên nghiệp, lịch sự và định dạng của câu trả lời."
        }

    async def _get_score(self, model: str, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        prompt = f"""Bạn là một giám khảo AI chuyên nghiệp. Hãy chấm điểm câu trả lời của một AI Agent dựa trên Ground Truth (Đáp án đúng).
Tiêu chí: {self.rubrics['accuracy']}

CÂU HỎI: {question}
GROUND TRUTH: {ground_truth}
CÂU TRẢ LỜI CỦA AGENT: {answer}

Hãy trả về theo định dạng JSON sau:
{{
    "score": <con số từ 1 đến 5>,
    "reasoning": "<lý giải ngắn gọn bằng tiếng Việt>"
}}"""

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
        )
        try:
            import json
            data = json.loads(response.choices[0].message.content)
            return {
                "score": float(data.get("score", 1.0)),
                "reasoning": data.get("reasoning", "N/A")
            }
        except:
            return {"score": 1.0, "reasoning": "Error parsing judge response."}

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        tasks = [self._get_score(model, question, answer, ground_truth) for model in self.models]
        results = await asyncio.gather(*tasks)
        
        individual_results = dict(zip(self.models, results))
        scores = [r["score"] for r in results]
        avg_score = sum(scores) / len(scores)
        
        # Agreement Rate
        max_diff = max(scores) - min(scores)
        agreement = max(0, 1.0 - (max_diff / 2.0))
        
        return {
            "final_score": avg_score,
            "agreement_rate": agreement,
            "individual_results": individual_results,
            "status": "consensus" if agreement >= 0.5 else "disagreement"
        }
