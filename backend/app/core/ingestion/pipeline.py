# Imports dependencies.
import uuid
from app.core.ingestion.chunker import document_chunker
from app.core.retrieval.embedding_loader import embedding_loader
from app.core.retrieval.qdrant_client import qdrant_db
from app.core.retrieval.neo4j_client import neo4j_db
from qdrant_client.http import models

class IngestionPipeline:
    def __init__(self):
        self.chunker = document_chunker
        self.embedder = embedding_loader
        self.qdrant = qdrant_db
        self.neo4j = neo4j_db

    def process_document(self, text: str, document_title: str):
        """
            The main pipeline: Chunks text -> Embeds it -> Saves to Qdrant & Neo4j.
        """
        print(f"Processing document: '{document_title}")

        # 1. Chop the text into chunks.
        chunks = self.chunker.chunk_text(text)
        print(f"Split into {len(chunks)} chunks.")

        doc_id = str(uuid.uuid4())

        # 2. Loop through each chunk.
        for i, chunk_text in enumerate(chunks):
            chunk_id = str(uuid.uuid4())

            # 3. Generate vectors (Dense for Qdrant, Sparse for Neo4j)
            dense_vec, sparse_vec = self.embedder.embed_text(chunk_text)

            # 4. Save to Qdrant (Vector DB)
            self._save_to_qdrant(chunk_id, dense_vec, chunk_text, document_title, i)

            # 5. Save to Neo4j (Graph DB)
            self._save_to_neo4j(doc_id, chunk_id, chunk_text, document_title, i)

        print("Document successfully ingested into both databases.")

    def _save_to_qdrant(self, chunk_id: str, dense_vec: list, text: str, title: str, chunk_index: int):
        self.qdrant.client.upsert(
            collection_name=self.qdrant.collection_name,
            points=[
                models.PointStruct(
                    id=chunk_id,
                    vector=dense_vec,
                    payload={"text": text, "title": title, "chunk_index": chunk_index}
                )
            ]
        )

    def _save_to_neo4j(self, doc_id: str, chunk_id: str, text: str, title: str, chunk_index: int):
        # Simple graph query: creates document node and chunk node, then connects them.
        query = """
        MERGE (d: Document {id: $doc_id, title: $title})
        CREATE (c: Chunk {id: $chunk_id, text: $text, index: $chunk_index})
        CREATE (d)-[:HAS_CHUNK]->(c)
        """
        with self.neo4j.driver.session() as session:
            session.run(query, doc_id=doc_id, title=title, chunk_id=chunk_id, text=text, chunk_index=chunk_index)

# Create Instance
ingestion_pipeline = IngestionPipeline()