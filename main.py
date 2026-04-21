import asyncio
import json
import os
import time
from typing import List, Dict, Any
from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgent
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge
from engine.retrieval_engine import LegalRetrievalEngine
from dotenv import load_dotenv

load_dotenv()

async def ensure_data_indexed():
    """
    Ensures data is indexed before running the benchmark.
    In a real scenario, this would check if the collection is populated.
    For this lab, we'll re-index the sample data.
    """
    if not os.path.exists("data/labor_law_sample.md"):
        print("❌ Missing data/labor_law_sample.md. Please create it first.")
        return
        
    engine = LegalRetrievalEngine()
    with open("data/labor_law_sample.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    docs = [{"metadata": {"title": "Bộ luật Lao động 2019", "id": "bllđ-2019"}, "content": content}]
    engine.index_documents(docs)

async def run_benchmark_with_results(agent_version: str, model_name: str, config: Dict[str, Any]):
    print(f"🚀 Khởi động Benchmark cho {agent_version} ({model_name})...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng.")
        return None, None

    # Initialize components with config
    agent = MainAgent(model=model_name, config=config)
    evaluator = RetrievalEvaluator()
    judge = LLMJudge()
    
    runner = BenchmarkRunner(agent, evaluator, judge)
    results = await runner.run_all(dataset)

    valid_results = [r for r in results if "error" not in r]
    
    if not valid_results:
        print("❌ All tests failed.")
        return results, None

    summary_metrics = {
        "avg_score": sum(r["judge"]["final_score"] for r in valid_results) / len(valid_results),
        "hit_rate": sum(r["ragas"]["hit_rate"] for r in valid_results) / len(valid_results),
        "agreement_rate": sum(r["judge"]["agreement_rate"] for r in valid_results) / len(valid_results)
    }
    return results, summary_metrics

async def main():
    # 1. Ensure Indexing
    print("--- 1. Cấu trúc lại Index ---")
    await ensure_data_indexed()
    
    # configs
    v1_config = {
        "system_prompt": "Trả lời câu hỏi ngắn gọn.",
        "top_k": 2
    }
    v2_config = {
        "system_prompt": "Bạn là một trợ lý pháp luật chuyên nghiệp. Hãy trả lời câu hỏi dựa trên văn bản trích lục. Nếu không thấy, hãy nói 'Tôi không tìm thấy thông tin này trong cơ sở dữ liệu'. Trích dẫn nguồn nếu có.",
        "top_k": 5
    }

    # 2. Run V1 (Base)
    v1_results, v1_metrics = await run_benchmark_with_results("V1", "gpt-4o-mini", v1_config)
    
    # 3. Run V2 (Optimized)
    v2_results, v2_metrics = await run_benchmark_with_results("V2", "gpt-4o-mini", v2_config)
    
    if not v1_metrics or not v2_metrics:
        print("⚠️ Không có đủ dữ liệu để so sánh.")
        return

    # 4. Final Reporting
    full_results = {
        "v1": v1_results,
        "v2": v2_results
    }
    
    final_summary = {
        "metadata": {
            "total": len(v1_results),
            "version": "OPTIMIZED (V2)",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "versions_compared": ["V1", "V2"]
        },
        "metrics": v2_metrics,
        "regression": {
            "v1": {
                "score": v1_metrics["avg_score"],
                "hit_rate": v1_metrics["hit_rate"],
                "judge_agreement": v1_metrics["agreement_rate"]
            },
            "v2": {
                "score": v2_metrics["avg_score"],
                "hit_rate": v2_metrics["hit_rate"],
                "judge_agreement": v2_metrics["agreement_rate"]
            },
            "decision": "RELEASE" if v2_metrics["avg_score"] >= v1_metrics["avg_score"] else "BLOCK"
        }
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(final_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)
    
    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    print(f"V1 Accuracy: {v1_metrics['avg_score']:.2f} | V2 Accuracy: {v2_metrics['avg_score']:.2f}")
    print(f"V1 Hit Rate: {v1_metrics['hit_rate']:.2f} | V2 Hit Rate: {v2_metrics['hit_rate']:.2f}")
    print(f"QUYẾT ĐỊNH: {final_summary['regression']['decision']}")

if __name__ == "__main__":
    asyncio.run(main())
