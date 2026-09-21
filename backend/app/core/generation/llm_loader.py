# Import dependencies.
import httpx

class OllamaClient:
    def __init__(self, model_name: str = "qwen3.5:latest", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.generate_endpoint = f"{self.base_url}/api/generate"

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
            Sends an async HTTP request to the local Ollama server and returns
            the generated text.
        """
        # Ollama expects JSON package with instructions.
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False     # We want the full response at once for now
        }

        # Using httpx to talk to ollama without blocking the FastAPI server.
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.generate_endpoint, json=payload)
                response.raise_for_status()
            
            except httpx.HTTPError as e:
                print(f"Error communicating with Ollama: {e}")
                return "Error: Could not generate response from Ollama."

# Create a singleton instance that our FastAPI app can import and use anywhere.
ollama_client = OllamaClient()