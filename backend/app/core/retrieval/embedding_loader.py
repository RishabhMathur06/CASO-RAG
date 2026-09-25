# Importing dependencies.
import os
from FlagEmbedding import BGEM3FlagModel

class EmbeddingLoader:
    def __init__(self):
        # Point to local models folder.
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "models", "bge-m3"
        )

        # Loads the model and tells it to use GPU (mps) if available.
        self.model = BGEM3FlagModel(model_path, use_fp16=True)

    def embed_text(self, text: str):
        """
            Takes a string of text and converts it into dense and sparse vectors
            for our databases to search.
        """
        # BGE-M3 can output both dense (Qdrant) and sparse (Neo4j) vectors at same time.
        embeddings = self.model.encode(
            [text],
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False
        )

        # Extracts the results from the list.
        dense_vector = embeddings['dense_vecs'][0].tolist()
        sparse_vector = embeddings['lexical_weights'][0]

        return dense_vector, sparse_vector

# Instance
embedding_loader = EmbeddingLoader()