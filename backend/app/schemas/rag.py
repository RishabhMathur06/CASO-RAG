# Imports dependencies.
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question or search query", min_length=3)
    top_k: int = Field(default=3, description="Number of context chunks to retrieve", ge=1, le=10)

class QueryResponse(BaseModel):
    query: str
    answer: str
    context: str

class IngestRequest(BaseModel):
    title: str = Field(..., description="Document title", min_length=1)
    text: str = Field(..., description="Full text content of the document", min_length=10)

class IngestResponse(BaseModel):
    status: str
    message: str
    title: str