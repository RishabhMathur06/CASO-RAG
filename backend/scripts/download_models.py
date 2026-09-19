# Importing dependencies.
import os
from huggingface_hub import snapshot_download

# Path to save the models.
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def download_embedding_models():
    """
        Downloads the BGE-M3 embedding model (for vector search) and 
        the BGE-Reranker model (for double-checking search results).
    """
    embed_repo = "BAAI/bge-m3"
    rerank_repo = "BAAI/bge-reranker-v2-m3"

    print(f"Downloading embedding model: {embed_repo}...")
    snapshot_download(repo_id=embed_repo, local_dir=os.path.join(MODEL_DIR, "bge-m3"))

    print(f"Downloading Reranker model: {rerank_repo}...")
    snapshot_download(repo_id=rerank_repo, local_dir=os.path.join(MODEL_DIR, "bge-reranker-v2-m3"))

    print("Embedding models successfully downloaded!")

if __name__ == "__main__":
    print("Starting Model Downloads...")
    download_embedding_models()
    print("All models downloaded successfully!")