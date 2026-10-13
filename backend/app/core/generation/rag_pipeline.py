# Imports dependencies.
from app.core.retrieval.search_engine import search_engine
from app.core.generation.prompt_builder import PromptBuilder
from app.core.generation.llm_loader import ollama_client

class RAGPipeline:
    def __init__(self):
        self.search_engine = search_engine
        self.prompt_builder = PromptBuilder()
        self.llm = ollama_client

    async def answer_query(self, query: str, top_k: int = 3) -> dict:
        """
        Executes the full RAG cycle:
        1. Retrieves relevant context from Qdrant & Neo4j.
        2. Builds an augmented prompt with strict anti-hallucination instructions.
        3. Generates a grounded answer via local Ollama.
        """
        # 1. Retrieve hybrid context from databases.
        context = self.search_engine.search(query=query, top_k=top_k)

        # 2. Build the grounded prompt.
        prompt, system_prompt = self.prompt_builder.build_rag_prompt(query=query, context=context)

        # 3. Ask local Ollama to generate the final answer.
        answer = await self.llm.generate(prompt=prompt, system_prompt=system_prompt)

        return {
            "query": query,
            "answer": answer,
            "context": context
        }

# Instance Creation.
rag_pipeline = RAGPipeline()