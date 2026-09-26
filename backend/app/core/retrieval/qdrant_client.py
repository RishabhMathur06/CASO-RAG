# Imports dependencies.
from qdrant_client import QdrantClient
from qdrant_client.http import models

class QdrantDBClient:
    def __init__(self, host: str = "localhost", port: int = 6333):
        # Connect to local Docker container running Qdrant.
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "caso_rag_docs"

        # The BGE-M3 model downloaded outputs dense vectors of exactly this size.
        self.vector_size = 1024

        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """
            Creates collection in the db if doesn't exists yet.
        """
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Created Qdrant collection: {self.collection_name}")

# Instance
qdrant_db = QdrantDBClient()