# Imports dependencies.
import os
from typing import Optional, Dict, Any
from loguru import logger
from langfuse import Langfuse

class LangfuseTracer:
    def __init__(self):
        # Read keys from environment.
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        self.host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
        self.enabled = bool(self.public_key and self.secret_key)

        if self.enabled:
            try:
                self.client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                    host=self.host
                )
                logger.success(f"Langfuse LLMOps tracer connected to: {self.host}")
            
            except Exception as e:
                logger.warning(f"Could not connect to Langfuse: {e}. Tracing will be disabled.")
                self.client = None
                self.enabled = False

        else:
            self.client = None
            logger.info("Langfuse keys not configured in '.env'. Running in offline tracing mode.")

    def log_rag_trace(
        self,
        query: str,
        answer: str,
        context: str,
        latency_seconds: float,
        cached: bool = False,
        model_name: str = "qwen3.5:latest"
    ):
        """
        Creates a trace in Langfuse containing the full RAG query lifecycle.
        """
        if not self.enabled or not self.client:
            return

        try:
            # 1. Create top-level trace.
            trace = self.client.trace(
                name="rag_query",
                input={"query": query},
                output={"answer": answer},
                metadata={"cached": cached, "latency_seconds": latency_seconds}
            )

            # 2. Record retrieval span.
            trace.span(
                name="context_retrieval",
                input={"query": query},
                output={"retrieved_context": context}
            )

            # 3. Record LLM generation event.
            trace.generation(
                name="ollama_generation",
                model=model_name,
                input=query,
                output=answer
            )

            # Flush events asynchronously.
            self.client.flush()

        except Exception as e:
            logger.warning(f"Failed to export trace to Langfuse: {e}")

# Instance Creation.
langfuse_tracer = LangfuseTracer()