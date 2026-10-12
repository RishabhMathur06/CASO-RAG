# Imports dependencies.
from app.core.retrieval.qdrant_client import qdrant_db
from app.core.retrieval.neo4j_client import neo4j_db
from app.core.retrieval.embedding_loader import embedding_loader

class HybridSearchEngine:
    def __init__(self):
        self.qdrant = qdrant_db
        self.neo4j = neo4j_db
        self.embedder = embedding_loader

    def search(self, query: str, top_k: int = 3):
        """
        The Hybrid Engine:
        1. Finds mathematical similarity in Qdrant
        2. Pulls graph relationships from Neo4j
        """
        print(f"\nSearching databases for: '{query}'")

        # 1. Turns the user's question into math (dense vector).
        dense_vec, _ = self.embedder.embed_text(query)

        # 2. Asks Qdrant to find the mathematically closest chunks.
        qdrant_results = self.qdrant.client.query_points(
            collection_name = self.qdrant.collection_name,
            query = dense_vec,
            limit = top_k
        )

        # Extract the unique IDs of the chunks Qdrant found.
        chunk_ids = [point.id for point in qdrant_results.points]

        if not chunk_ids:
            return "No relevant context found in databases."

        # 3. Ask Neo4j to pull those exact chunks AND their relationships
        # We find the chunks and also ask "What Document does this belong to?"
        graph_query = """
        MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
        WHERE c.id IN $chunk_ids
        RETURN c.text AS text, d.title AS title
        """

        context_blocks = []
        with self.neo4j.driver.session() as session:
            results = session.run(graph_query, chunk_ids=chunk_ids)

            for record in results:
                # We format the context beautifully for the LLM.
                block = f"[Source: {record['title']}]\n{record['text']}"
                context_blocks.append(block)

        # 4. Mash all the context together into one giant string.
        final_context = "\n\n---\n\n".join(context_blocks)
        
        return final_context

# Instance creation
search_engine = HybridSearchEngine()