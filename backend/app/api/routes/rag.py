# Imports dependencies.
from fastapi import APIRouter, HTTPException, status
from app.schemas.rag import QueryRequest, QueryResponse, IngestRequest, IngestResponse
from app.core.generation.rag_pipeline import rag_pipeline
from app.core.ingestion.pipeline import ingestion_pipeline

router = APIRouter(prefix="/rag", tags=["RAG Engine"])

@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_rag(request: QueryRequest):
    """
    Answers user queries using the Hybrid GraphRAG pipeline:
    1. Vector similarity search in Qdrant
    2. Knowledge graph traversal in Neo4j
    3. Grounded answer generation via Ollama (Qwen)
    """
    try:
        result = await rag_pipeline.answer_query(query=request.query, top_k=request.top_k)

        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing RAG query: {str(e)}"
        )

@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(request: IngestRequest):
    """
    Ingests a raw document into both Qdrant (vectors) and Neo4j (graph).
    """
    try:
        ingestion_pipeline.process_document(text=request.text, document_title=request.title)

        return IngestResponse(
            status="success",
            message="Document successfully processed and indexed into the Vector and Graph DBs.",
            title=request.title
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting document: {str(e)}"
        )