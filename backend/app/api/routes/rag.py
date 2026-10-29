# Imports dependencies.
from fastapi import APIRouter, HTTPException, status
from app.schemas.rag import QueryRequest, QueryResponse, IngestRequest, IngestResponse
from app.core.generation.rag_pipeline import rag_pipeline
from app.core.ingestion.pipeline import ingestion_pipeline
from app.core.cache.redis_cache import redis_query_cache
import time
from app.llmops.metrics import RAG_QUERIES_TOTAL, RAG_QUERY_DURATION_SECONDS, RAG_DOCS_INGESTED_TOTAL

router = APIRouter(prefix="/rag", tags=["RAG Engine"])

@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_rag(request: QueryRequest):
    """
    Answers user queries using the Hybrid GraphRAG pipeline with Redis caching:
    1. Checks Redis cache (returns in < 15ms on hit)
    2. On cache miss: Vector search (Qdrant) + Graph traversal (Neo4j)
    3. Cross-Encoder reranking (BGE-Reranker-v2-m3)
    4. Grounded answer generation via Ollama (Qwen)
    """
    try:
        start_time = time.perf_counter()
        result = await rag_pipeline.answer_query(query=request.query, top_k=request.top_k)
        duration = time.perf_counter() - start_time

        # Track query latency and counts metrics.
        is_cached = str(result.get("cached", False)).lower()
        RAG_QUERIES_TOTAL.labels(status="success", cached=is_cached).inc()
        RAG_QUERY_DURATION_SECONDS.labels(cached=is_cached).observe(duration)

        return QueryResponse(**result)
    
    except Exception as e:
        RAG_QUERIES_TOTAL.labels(status="error", cached="False").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing RAG query: {str(e)}"
        )

@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(request: IngestRequest):
    """
    Ingests a raw document into both Qdrant (vectors) and Neo4j (graph).
    """
    try:
        ingestion_pipeline.process_document(text=request.text, document_title=request.title)

        # Track document ingestion.
        RAG_DOCS_INGESTED_TOTAL.inc()
        
        # Invalidate cache when a document is ingested.
        await redis_query_cache.clear_all()

        return IngestResponse(
            status="success",
            message="Document successfully processed and indexed into the Vector and Graph DBs.",
            title=request.title
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting document: {str(e)}"
        )

# Manual cache clear endpoint.
@router.delete("/cache", status_code=status.HTTP_200_OK)
async def clear_cache():
    """
    Manually invalidates and clears all cached RAG queries from Redis.
    """
    try:
        cleared_count = await redis_query_cache.clear_all()

        return {
            "status": "success",
            "message": f"Successfully cleared {cleared_count} cached queries from Redis."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )