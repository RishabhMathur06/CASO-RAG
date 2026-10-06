# Imports dependencies.
from app.core.ingestion.pipeline import ingestion_pipeline
from app.core.retrieval.neo4j_client import neo4j_db
from app.core.retrieval.qdrant_client import qdrant_db

# Tiny test document:
sample_text = """
Steve Jobs was an American entrepreneur, inventor, and investor best known as the co-founder of Apple Inc. 
He was born in San Francisco, California. 
Apple was founded in 1976 to sell Wozniak's Apple I personal computer.
"""

print("\nStarting Ingestion Test...")
ingestion_pipeline.process_document(sample_text, "Biography of Steve Jobs")

print("\n--- Verify Qdrant (Vector Database) ---")
qdrant_count = qdrant_db.client.count(collection_name=qdrant_db.collection_name).count
print(f"Total chunks stored in Qdrant: {qdrant_count}")

print("\n--- Verifying Neo4j (Graph Database) ---")
with neo4j_db.driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) as count")
    neo4j_count = result.single()["count"]
    print(f"Total nodes stored in Neo4j: {neo4j_count}")

print("\nTest Complete!")