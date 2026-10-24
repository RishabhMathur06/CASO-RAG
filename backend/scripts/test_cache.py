# Imports dependencies.
import time
import asyncio
from loguru import logger
from app.core.generation.rag_pipeline import rag_pipeline
from app.core.cache.redis_cache import redis_query_cache

async def run_cache_benchmark():
    logger.info("=== Starting Redis Caching Latency Benchmark ====")

    # 0. Clear existing cache for a clean benchmark run.
    await redis_query_cache.clear_all()

    test_query = "Where was Steve Jobs born and what was Apple's first product in 1976?"

    # --- RUN 1: Cold Query (Cache Miss) ---
    logger.info("\n--- [Run 1] Cold Query (Expecting Cache Miss & Live Generation) ---")
    start_time = time.perf_counter()
    
    response_1 = await rag_pipeline.answer_query(query=test_query, top_k=2)

    cold_duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(f"Run 1 completed in: {cold_duration_ms: .2f} ms")
    logger.info(f"Run 1 cached flag: {response_1.get('cached')}")
    assert response_1.get("cached") is False, "Run 1 must be a cache miss!"

    # --- RUN 2: Warm Query (Cache Hit) ---
    logger.info("\n--- [Run 2] Identical Query (Expecting Instant Cache Hit) ---")
    start_time = time.perf_counter()

    response_2 = await rag_pipeline.answer_query(query=test_query, top_k=2)

    cached_duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(f"Run 2 completed in: {cached_duration_ms: .2f} ms")
    logger.info(f"Run 2 cached flag: {response_2.get('cached')}")
    assert response_2.get("cached") is True, "Run 2 must be a cache hit!"

    # Ensure answers match.
    assert response_1["answer"] == response_2["answer"], "Cached answer must match original answer!"

    # --- Latency & Performance Summary ---
    speedup = cold_duration_ms / max(cached_duration_ms, 0.001)
    latency_reduction = ((cold_duration_ms - cached_duration_ms) / cold_duration_ms) * 100

    print("\n" + "="*60)
    print("📊 REDIS CACHING PERFORMANCE BENCHMARK RESULTS")
    print("="*60)
    print(f"• Cold Query Latency (Live RAG) : {cold_duration_ms:.2f} ms")
    print(f"• Cached Query Latency (Redis)  : {cached_duration_ms:.2f} ms")
    print(f"• Speedup Factor                : {speedup:.1f}x FASTER")
    print(f"• Latency Reduction             : {latency_reduction:.2f}%")
    print("="*60)

    logger.success("Redis caching benchmark passed all assertions successfully!")

if __name__ == "__main__":
    asyncio.run(run_cache_benchmark())