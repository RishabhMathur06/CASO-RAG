# Imports dependencies.
import time
from fastapi import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# 1. Query Counter: Tracks total queries, sliced by status and cache status.
RAG_QUERIES_TOTAL = Counter(
    "caso_rag_queries_total",
    "Total count of queries processed by CASO-RAG",
    ["status", "cached"]
)

# 2. Latency Histogra: Measures exact latency distribution (p50, p90, p99)
RAG_QUERY_DURATION_SECONDS = Histogram(
    "caso_rag_query_duration_seconds",
    "Latency of RAG queries in seconds",
    ["cached"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# 3. Ingestion Counter: Tracks total documents ingested into Qdrant & Neo4j
RAG_DOCS_INGESTED_TOTAL = Counter(
    "caso_rag_documents_ingested_total",
    "Total count of documents ingested into vector and graph databases"
)

def get_metrics_response() -> Response:
    """
    Scrape endpoint handler that formats all registered metrics
    into the standard Prometheus text format.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)