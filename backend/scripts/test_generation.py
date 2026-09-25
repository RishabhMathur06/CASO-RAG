import asyncio

from app.core.generation.llm_loader import ollama_client
from app.core.generation.prompt_builder import PromptBuilder

async def main():
    print("Testing connection to Ollama...")

    query = "What is the capital of France?"
    context = "France is a country in Western Europe. Its capital is Paris."

    # Uses Prompt Builder to combine the query and context.
    prompt, system = PromptBuilder.build_rag_prompt(query, context)

    print("Sending prompt to qwen3.5:latest...")

    # Sends the request to Ollama.
    response = await ollama_client.generate(prompt=prompt, system_prompt=system)

    print("\nOllama replied:")
    print("-" * 50)
    print(response)
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())