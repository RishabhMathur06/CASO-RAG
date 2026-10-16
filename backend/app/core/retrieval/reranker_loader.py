# Imports dependencies.
import os
from typing import List, Dict, Any
from loguru import logger
from FlagEmbedding import FlagReranker

class RerankerLoader:
    def __init__(self):
        # Resolve local path to bge-reranker-v2-m3
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "models", "bge-reranker-v2-m3"
        )

        logger.info(f"Loading Cross-Encoder Reranker from: {self.model_path}")

        # use_fp16 = True provides fast memory-efficient inference on Apple Silicon/GPUs
        self.reranker = FlagReranker(self.model_path, use_fp16=True)
        logger.success("Cross-encoder Reranker loaded successfully!")

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Takes a user query and a list of candidate chunk dicts,
        computes cross-encoder relevance scores, and returns the top_k sorted candidates.
        
        Each candidate dictionary should contain at least:
        {"text": "...", "title": "...", "chunk_id": "..."}
        """
        if not candidates:
            logger.warning("Reranker received an empty candidate list.")
            return []

        # Prepare sentence pairs for cross-attention scoring : [query, document_text].
        sentence_pairs = [[query, candidate["text"]] for candidate in candidates]

        logger.debug(f"Computing cross-encoder scores for {len(sentence_pairs)} candidates against query: '{query[:50]}...'")

        # normalize=True applies sigmoid to map raw logits to [0.0, 1.0] probabilities.
        scores = self.reranker.compute_score(sentence_pairs, normalize=True)

        # In case a single candidate was passed, ensure scores is a list.
        if isinstance(scores, float):
            scores = [scores]

        # Attach score to candidate dictionaries.
        scored_candidates = []
        for candidate, score in zip(candidates, scores):
            candidate_copy = dict(candidate)
            candidate_copy["rerank_score"] = round(float(score), 4)
            scored_candidates.append(candidate_copy)

        # Sort descending by rerank_score.
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

        top_candidates = scored_candidates[:top_k]

        for idx, item in enumerate(top_candidates):
            logger.info(
                f"[Rank {idx+1}] Score: {item['rerank_score']:.4f} | Source: '{item.get('title', 'Uknown')}' | "
                f"Snippet: {item['text'][:60].strip()}..."
            )

        return top_candidates

# Instance creation
reranker_loader = RerankerLoader()