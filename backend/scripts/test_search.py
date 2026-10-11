# Imports dependencies.
from app.core.retrieval.search_engine import search_engine

# Query related to "steve Jobs" document we ingested earlier:
test_query = "Where was Steve Jobs born and what did Apple sell in 1976?"

print("--- Testing Hybrid Search Engine ---")
context = search_engine.search(query=test_query, top_k=2)

print("\n--- Retrieved Context ---")
print(context)
print("\nSearch Test Complete!")