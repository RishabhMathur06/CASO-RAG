# Importing dependencies
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, SparseVectorParams
from app.config import get_settings

settings = get_settings()

# Initializes the async Qdrant client
qdrant = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

async def init_qdrant():
    """
        Initializes the Qdrant colleciton for dense and sparse
        vectors if it doesn't exist.
    """
    collection_name = settings.qdrant_collection_name
    exists = await qdrant.collection_exists(collection_name)

    if not exists:
        await qdrant.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(size=1024, distance=Distance.COSINE)
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams()
            }
        )
        print(f"Created Qdrant Collection: {collection_name}")
    else:
        print(f"Qdrant Collection {collection_name} already exists.")