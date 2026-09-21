class PromptBuilder:
    @staticmethod
    def build_rag_prompt(query: str, context: str) -> tuple[str, str]:
        """
            Combines the user query and database  context into a format
            Ollama understands.

            Returns a tuple of (prompt, system_prompt) 
        """
        system_prompt = """You are a highly intelligent, precise and helful AI assistant.
        Your goal is to answer the user's question based strictly on the context provided.
        If the context does not contain the answer, politely state that you do not have enough
        information. Do not hallucinate or make up facts.
        """

        prompt = f"""Use the following context to answer the question.

        CONTEXT:
        {context}

        QUESTION:
        {query}

        ANSWER:"""

        return prompt, system_prompt