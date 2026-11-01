# Imports dependencies.
import time
import asyncio
import mlflow
from loguru import logger

from app.core.ingestion.pipeline import ingestion_pipeline
from app.core.retrieval.qdrant_client import qdrant_db
from app.core.retrieval.neo4j_client import neo4j_db
from app.core.retrieval.embedding_loader import embedding_loader
from app.core.retrieval.reranker_loader import reranker_loader
from app.core.cache.redis_cache import redis_query_cache
from app.core.generation.rag_pipeline import rag_pipeline

# 1. Knowledge Corpus (Includes True Sources + Distractor Documents)
CORPUS = [
    {
        "title": "Biography of Steve Jobs",
        "text": "Steve Jobs was an American entrepreneur and inventor best known as the co-founder of Apple Inc. He was born in San Francisco, California. Apple was founded in 1976 to sell Wozniak's Apple I personal computer."
    },
    {
        "title": "California Apple Orchard Report 1976",
        "text": "In 1976, apple orchards across Northern California and San Francisco reported record harvests of red delicious apples sold in local markets and farm stands."
    },
    {
        "title": "Steve Wozniak Engineering Notes",
        "text": "The Apple I personal computer was designed and hand-built by Steve Wozniak. It utilized the MOS Technology 6502 microprocessor running at 1 MHz with 4 KB of standard RAM."
    },
    {
        "title": "History of Python",
        "text": "Python is a high-level programming language conceived in the late 1980s by Guido van Rossum at CWI in the Netherlands. It was officially released in 1991."
    },
    {
        "title": "Monty Python British Comedy",
        "text": "Monty Python was a British surreal comedy troupe formed in 1969. Their sketch show aired on the BBC and influenced modern comedy across Europe and the Netherlands."
    },
    {
        "title": "Neo4j Graph Architecture",
        "text": "Neo4j is a native graph database that stores data as nodes and relationships rather than tables. It uses the declarative Cypher query language for multi-hop graph traversals."
    },
    {
        "title": "Qdrant Vector Engine",
        "text": "Qdrant is a high-performance vector similarity search engine written in Rust. It uses Hierarchical Navigable Small World (HNSW) indexes and cosine distance for fast nearest-neighbor retrieval."
    }
]

# 2. Evaluation Benchmark Queries & Ground-Truth Expected Document Titles
EVAL_QUERIES = [
    {
        "query": "In 1976 in San Francisco, what product was Apple founded to sell?",
        "expected_title": "Biography of Steve Jobs"
    },
    {
        "query": "Which microprocessor and how much RAM did the Apple I computer use?",
        "expected_title": "Steve Wozniak Engineering Notes"
    },
    {
        "query": "Who conceived the Python language in the Netherlands and when was it released?",
        "expected_title": "History of Python"
    },
    {
        "query": "What query language is used to traverse nodes and relationships in a graph database?",
        "expected_title": "Neo4j Graph Architecture"
    },
    {
        "query": "Which Rust-based engine uses HNSW indexes for nearest-neighbor vector search?",
        "expected_title": "Qdrant Vector Engine"
    }
]

def evaluate_baseline_dense(query: str, top_k: int = 3) -> list[dict]:
    """
    Simulates a standard 'Dumb' Dense-Only RAG retrieval (Qdrant vector search only, no reranker).
    """
    dense_vec, _ = embedding_loader.embed_text(query)
    res = qdrant_db.client.query_points(
        collection_name=qdrant_db.collection_name,
        query=dense_vec,
        limit=top_k
    )

    return [
        {"title": pt.payload.get("title", ""), "text": pt.payload.get("text", "")} for pt in res.points
    ]

def evaluate_caso_rag_retrieval(query: str, top_k: int = 3, min_score: float = 0.20) -> list[dict]:
    """
    Runs CASO-RAG 2-Stage Retrieval (Qdrant + Neo4j Graph + BGE Cross-Encoder Reranker + Cutoff).
    """
    dense_vec, _ = embedding_loader.embed_text(query)
    res = qdrant_db.client.query_points(
        collection_name=qdrant_db.collection_name,
        query=dense_vec,
        limit=10
    )

    chunk_ids = [pt.id for pt in res.points]
    if not chunk_ids:
        return []

    graph_query = """
    MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
    WHERE c.id IN $chunk_ids
    RETURN c.id AS chunk_id, c.text AS text, d.title AS title
    """

    candidates = []
    with neo4j_db.driver.session() as session:
        records = session.run(graph_query, chunk_ids=chunk_ids)
        for r in records:
            candidates.append({
                "chunk_id": r["chunk_id"],
                "text": r["text"],
                "title": r["title"]
            })

    reranked = reranker_loader.rerank(query=query, candidates=candidates, top_k=top_k)
    filtered = [c for c in reranked if c["rerank_score"] >= min_score]

    return filtered if filtered else reranked[:1]

def compute_rank_metrics(results_per_query: list[tuple[list[dict], str]]):
    """
    Compute Top-1 Hit Rate, Recall@3, MRR and Noise Chunks Passed.
    """
    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_ranks = []
    irrelevant_chunks_passed = 0

    for retrieved, expected_title in results_per_query:
        titles = [item["title"] for item in retrieved]

        # Count irrelevant distractor chunks included in the final context.
        for t in titles:
            if t != expected_title:
                irrelevant_chunks_passed += 1

        if titles and titles[0] == expected_title:
            hits_at_1 += 1

        if expected_title in titles[:3]:
            hits_at_3 += 1
            rank = titles.index(expected_title) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)
    
    n = len(results_per_query)

    return {
        "hit_at_1": (hits_at_1 / n) * 100,
        "recall_at_3": (hits_at_3 / n) * 100,
        "mrr": sum(reciprocal_ranks) / n,
        "noise_chunks": irrelevant_chunks_passed
    }

async def main():
    logger.info("=== Starting Phase 9: CASO-RAG Quantitative Benchmark ===")

    # 1. Seed Corpus
    logger.info("Ingesting benchmark corpus into Qdrant and Neo4j...")
    for doc in CORPUS:
        ingestion_pipeline.process_document(text=doc["text"], document_title=doc["title"])

    # 2. Run baseline vs CASO-RAG Retrieval
    baseline_runs = []
    casorag_runs = []

    for item in EVAL_QUERIES:
        q = item["query"]
        expected = item["expected_title"]

        base_res = evaluate_baseline_dense(q, top_k=3)
        caso_res = evaluate_caso_rag_retrieval(q, top_k=3, min_score=0.20)

        baseline_runs.append((base_res, expected))
        casorag_runs.append((caso_res, expected))

    base_metrics = compute_rank_metrics(baseline_runs)
    caso_metrics = compute_rank_metrics(casorag_runs)

    # Calculate percentage improvements
    noise_reduction_pct = (
        ((base_metrics["noise_chunks"] - caso_metrics["noise_chunks"]) / max(base_metrics["noise_chunks"], 1))*100
    )

    # 3. Latency Benchmark (Cold vs Redis Cached)
    await redis_query_cache.clear_all()
    sample_q = EVAL_QUERIES[0]["query"]

    t0 = time.perf_counter()
    await rag_pipeline.answer_query(sample_q, top_k=2)
    cold_ms = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    await rag_pipeline.answer_query(sample_q, top_k=2)
    cached_ms = (time.perf_counter() - t1) * 1000

    # 4. Log to MLFlow (if running on port 5001, else fallback to local)
    try:
        mlflow.set_tracking_uri("http://localhost:5001")
        mlflow.set_experiment("CASO-RAG-Benchmark")
        with mlflow.start_run(run_name="Baseline_vs_CASO_RAG"):
            mlflow.log_params({
                "embedding_model": "BAAI/bge-m3",
                "reranker_model": "BAAI/bge-reranker-v2-m3",
                "min_score_threshold": 0.20,
                "num_eval_queries": len(EVAL_QUERIES)
            })
            mlflow.log_metrics({
                "baseline_hit_at_1": base_metrics["hit_at_1"],
                "casorag_hit_at_1": caso_metrics["hit_at_1"],
                "baseline_mrr": base_metrics["mrr"],
                "casorag_mrr": caso_metrics["mrr"],
                "noise_reduction_pct": noise_reduction_pct,
                "cold_latency_ms": cold_ms,
                "cached_latency_ms": cached_ms
            })
        logger.success("Benchmark metrics logged to MLflow server at http://localhost:5001")
    except Exception as e:
        logger.warning(f"MLflow server not reachable ({e}). Skipping remote MLflow log.")

    # 5. Print final resume-ready report
    print("\n" + "=" * 68)
    print("🏆 CASO-RAG QUANTITATIVE BENCHMARK REPORT (RESUME METRICS)")
    print("=" * 68)
    print(f"{'Metric':<32} | {'Dense Baseline':<15} | {'CASO-RAG':<15}")
    print("-" * 68)
    print(f"{'Top-1 Accuracy (Hit@1)':<32} | {base_metrics['hit_at_1']:>13.1f}% | {caso_metrics['hit_at_1']:>13.1f}%")
    print(f"{'Recall@3':<32} | {base_metrics['recall_at_3']:>13.1f}% | {caso_metrics['recall_at_3']:>13.1f}%")
    print(f"{'Mean Reciprocal Rank (MRR)':<32} | {base_metrics['mrr']:>14.3f} | {caso_metrics['mrr']:>14.3f}")
    print(f"{'Irrelevant Noise Chunks Passed':<32} | {base_metrics['noise_chunks']:>14d} | {caso_metrics['noise_chunks']:>14d}")
    print("-" * 68)
    print(f"• Distractor / Noise Reduction  : {noise_reduction_pct:.1f}% fewer irrelevant chunks sent to LLM")
    print(f"• Cold Pipeline Latency         : {cold_ms:.2f} ms")
    print(f"• Redis Cached Latency          : {cached_ms:.2f} ms ({cold_ms / max(cached_ms, 0.01):.0f}x speedup)")
    print("=" * 68 + "\n")

if __name__ == "__main__":
    asyncio.run(main())