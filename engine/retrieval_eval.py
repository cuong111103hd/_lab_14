from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Hit Rate: 1.0 if at least one expected_id is in retrieved_ids[:top_k], else 0.0.
        """
        if not expected_ids:
            return 0.0
        
        # In many implementations, expected_ids might be a list of one or more "correct" IDs.
        # retrieved_ids is a list of IDs returned by the search engine.
        top_retrieved = retrieved_ids[:top_k]
        for eid in expected_ids:
            if eid in top_retrieved:
                return 1.0
        return 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Mean Reciprocal Rank: 1 / rank of the first expected_id in retrieved_ids.
        """
        if not expected_ids:
            return 0.0
            
        for rank, rid in enumerate(retrieved_ids, start=1):
            if rid in expected_ids:
                return 1.0 / rank
        return 0.0

    async def score(self, test_case: Dict, agent_response: Dict) -> Dict:
        """
        Interface for BenchmarkRunner.
        """
        expected_ids = test_case.get("expected_retrieval_ids", [])
        retrieved_ids = agent_response.get("retrieved_ids", [])
        
        return {
            "hit_rate": self.calculate_hit_rate(expected_ids, retrieved_ids),
            "mrr": self.calculate_mrr(expected_ids, retrieved_ids)
        }
