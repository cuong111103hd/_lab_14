import asyncio
import time
from typing import List, Dict, Any

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()
        
        # 1. Call Agent
        try:
            response = await self.agent.query(test_case["question"])
            latency = time.perf_counter() - start_time
        except Exception as e:
            latency = time.perf_counter() - start_time
            return {
                "test_case": test_case["question"],
                "error": str(e),
                "status": "error",
                "latency": latency
            }
        
        # 2. Run Retrieval Evaluation
        retrieval_metrics = await self.evaluator.score(test_case, response)
        
        # 3. Run Multi-Judge
        judge_result = await self.judge.evaluate_multi_judge(
            test_case["question"], 
            response["answer"], 
            test_case.get("expected_answer", "")
        )
        
        return {
            "test_case": test_case["question"],
            "agent_response": response["answer"],
            "latency": latency,
            "ragas": {
                "hit_rate": retrieval_metrics["hit_rate"],
                "mrr": retrieval_metrics.get("mrr", 0.0),
                "faithfulness": 0.9, # Mock as requested in schema
                "relevancy": 0.8     # Mock as requested in schema
            },
            "judge": judge_result,
            "status": "pass" if judge_result["final_score"] >= 3 else "fail"
        }

    async def run_all(self, dataset: List[Dict], batch_size: int = 10) -> List[Dict]:
        """
        Runs in parallel batches.
        """
        results = []
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        return results
