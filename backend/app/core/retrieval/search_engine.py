# Imports dependencies.
from typing import List, Dict, Any
from loguru import logger

from app.core.retrieval.qdrant_client import qdrant_db
from app.core.retrieval.neo4j_client import neo4j_db
from app.core.retrieval.embedding_loader import embedding_loader
from app.core.retrieval.reranker_loader import reranker_loader

class HybridSearchEngine:
    def __init__(self):
        self.qdrant = qdrant_db
        self.neo4j = neo4j_db
        self.embedder = embedding_loader
        self.reranker = reranker_loader

    def search(self, query: str, top_k: int = 3, min_score: float = 0.20) -> str:
        """
        The 2-stage Hybrid GraphRAG Engine:
        1. STAGE-1 (Recall): Vector search in Qdrant + Graph traversal in Neo4j (fetch broad candidate pool).
        2. STAGE-2 (Precision): Cross-encoder reranking via BGE-Reranker-v2-m3 with score threshold filtering.
        """
        logger.info(f"Initiating Hybrid Search for query: '{query}'")

        # 1. Turns the user's question into math (dense vector).
        dense_vec, _ = self.embedder.embed_text(query)

        # Stage 1: Fetch a wider candidate pool (at least 10 candidates or 3x top_k)
        candidate_limit = max(top_k * 3, 10)
        logger.debug(f"Stage 1: Fetching up to {candidate_limit} candidates from Qdrant...")

        # 2. Asks Qdrant to find the mathematically closest chunks.
        qdrant_results = self.qdrant.client.query_points(
            collection_name = self.qdrant.collection_name,
            query = dense_vec,
            limit = candidate_limit
        )

        # Extract the unique IDs of the chunks Qdrant found.
        chunk_ids = [point.id for point in qdrant_results.points]

        if not chunk_ids:
            logger.warning(f"No vector matches found in Qdrant for query: '{query}'")
            return "No relevant context found in databases."

        # Fetch Graph relationships and text from Neo4j for all candidate chunks.
        # We find the chunks and also ask "What Document does this belong to?"
        graph_query = """
        MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
        WHERE c.id IN $chunk_ids
        RETURN c.id AS chunk_id, c.text AS text, d.title AS title
        """

        candidates = []
        with self.neo4j.driver.session() as session:
            results = session.run(graph_query, chunk_ids=chunk_ids)
            for record in results:
                candidates.append({
                    "chunk_id": record["chunk_id"],
                    "text": record["text"],
                    "title": record["title"]
                })

        logger.info(f"Stage 1 complete: Retrieved {len(candidates)} candidate chunks with Neo4j graph lineage.")

        # Stage 2: Cross-Encoder Reranking.
        logger.debug(f"Stage 2: Reranking candidates to pick top {top_k} highest-relevance chunks...")
        reranked_chunks = self.reranker.rerank(query=query, candidates=candidates, top_k=top_k)

        # Filter out chunks that do not meet the minimum relevance threshold
        filtered_chunks = [c for c in reranked_chunks if c["rerank_score"] >= min_score]

        if not filtered_chunks and reranked_chunks:
            logger.warning(f"No candidate met the threshold ({min_score}). Falling back to top 1 candidate.")
            filtered_chunks = reranked_chunks[:1]

        logger.info(f"Retained {len(filtered_chunks)} chunks meeting the relevance threshold (>= {min_score}).")

        # Build final formatted context string for LLM.
        context_blocks = []
        for chunk in filtered_chunks:
            block = f"[Source: {chunk['title']} | Relevance Score: {chunk['rerank_score']:.4f}]\n{chunk['text']}"
            context_blocks.append(block)

        if not context_blocks:
            return "No relevant context found in databases."

        final_context = "\n\n---\n\n".join(context_blocks)
        return final_context

# Instance creation
search_engine = HybridSearchEngine()