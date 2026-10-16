# Imports dependencies.
from app.core.retrieval.reranker_loader import reranker_loader
from loguru import logger

def test_reranker_standalone():
    logger.info("--- Starting Standalone Reranker Verification Test ---")

    query = "What is the capital of France and what is its famous landmark?"

    candidates = [
        {
            "chunk_id": "1",
            "title": "Geography of Europe",
            "text": "Paris is the capital and most populous city of France, known for the Eiffel Tower."
        },
        {
            "chunk_id": "2",
            "title": "Automotive Engineering",
            "text": "The internal combustion engine generates mechanical power through the combustion of fuel."
        },
        {
            "chunk_id": "3",
            "title": "French Tourism Guide",
            "text": "France attracts millions of visitors each year to it's vineyards, museums and historic chateaux in the Loire Valley."
        }
    ]

    results = reranker_loader.rerank(query=query, candidates=candidates, top_k=2)

    logger.info("--- Results Summary ---")

    for r in results:
        print(f"Ranked Score: {r['rerank_score']} -> {r['title']}")

    # Validation assertions.
    assert len(results) == 2, "Expected top 2 candidates."
    assert results[0]["chunk_id"] == "1", "Candidate 1 (Paris/Eiffel) must have the highest score!"
    assert results[0]["rerank_score"] > results[1]["rerank_score"], "Top candidate must strictly outscore candidate 2."

    logger.success("All Reranker tests passed successfully!")

if __name__ == "__main__":
    test_reranker_standalone()