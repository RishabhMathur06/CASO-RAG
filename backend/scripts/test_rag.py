# Imports dependencies.
import asyncio
from app.core.generation.rag_pipeline import rag_pipeline

async def main():
    print("--- Testing full end-to-end RAG pipeline ---")
    query = "Where was Steve Jobs born and what was Apple's first product in 1976?"

    result = await rag_pipeline.answer_query(query=query)

    print("\n[QUESTION]:")
    print(result["query"])
    print("\n[RETRIEVED CONTEXT]:")
    print(result["context"])
    print("\n[LLM GENERATED ANSWER]:")
    print(result["answer"])
    print("\n--- RAG Test Complete! ---")

if __name__ == "__main__":
    asyncio.run(main())