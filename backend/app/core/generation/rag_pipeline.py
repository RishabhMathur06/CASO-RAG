# Imports dependencies.
from loguru import logger
from app.core.retrieval.search_engine import search_engine
from app.core.generation.prompt_builder import PromptBuilder
from app.core.generation.llm_loader import ollama_client
from app.core.cache.redis_cache import redis_query_cache

import time
from app.llmops.tracer import langfuse_tracer

class RAGPipeline:
    def __init__(self):
        self.search_engine = search_engine
        self.prompt_builder = PromptBuilder()
        self.llm = ollama_client
        self.cache = redis_query_cache
        self.tracer = langfuse_tracer

    async def answer_query(self, query: str, top_k: int = 3) -> dict:
        """
        Executes the full RAG cycle:
        1. Checks Redis cache (return instantly on hit).
        2. On cache miss: retrieves hybrid context from Qdrant & Neo4j.
        3. Builds an augmented prompt with strict anti-hallucination instructions and generates a grounded answer via local Ollama.
        4. Saves response into Redis cache for future queries.
        """
        start_time = time.perf_counter()

        # 1. Check Redis cache first.
        cached_result = await self.cache.get(query=query, top_k=top_k)
        if cached_result:
            self.tracer.log_rag_trace(
                query=query,
                answer=cached_result["answer"],
                context=cached_result["context"],
                latency_seconds=time.perf_counter() - start_time,
                cached=True
            )

            return cached_result

        # 2. Cache miss: retrieve hybrid context from databases.
        logger.info(f"Executing live RAG generation for: '{query}'")
        context = self.search_engine.search(query=query, top_k=top_k)

        # 3. Build grounded prompt.
        prompt, system_prompt = self.prompt_builder.build_rag_prompt(query=query, context=context)

        # 4. Generate the final answer via Ollama's locall LLMs.
        answer = await self.llm.generate(prompt=prompt, system_prompt=system_prompt)

        result = {
            "query": query,
            "answer": answer,
            "context": context,
            "cached": False
        }
        
        # 5. Store in Redis cache for future calls.
        await self.cache.set(query=query, top_k=top_k, data=result)

        self.tracer.log_rag_trace(
            query=query,
            answer=answer,
            context=context,
            latency_seconds=time.perf_counter() - start_time,
            cached=False
        )

        return result

# Instance Creation.
rag_pipeline = RAGPipeline()