# Import dependencies.
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.db.qdrant_client import init_qdrant
from app.db.neo4j_client import neo4j_db
from app.db.redis_client import check_redis_connection

from app.api.routes import health

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function manages the startup and shutdown lifecycle of the app.
    Everything before 'yield' runs when the server turns on.
    Everything after 'yield' runs when the server turns off.
    """
    logger.info("Starting up CASO-RAG server...")

    # Initializes Vector Database (Qdrant).
    await init_qdrant()

    # Connects to Graph Database (Neo4j) and set schema rules.
    await neo4j_db.connect()
    await neo4j_db.init_constraints()

    # Check Cache connection (Redis)
    await check_redis_connection()

    logger.info("All database connections established successfully!")

    # Server runs and handles user requests while paused here.
    yield

    logger.info("Shutting down CASO-RAG server...")

    # Cleans up connections gracefully.
    await neo4j_db.close()
    logger.info("Shutdown complete.")

# Initializes the FastAPI Application.
app = FastAPI(
    title="CASO-RAG API",
    version="1.0.0",
    description="A Self-Organizing, Context-Aware Hybrid Graph-Vector Retrieval Engine",
    lifespan=lifespan
)

# Sets up CORS.
# Allows our React frontend to talk to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plugs the health router into main app and automaticlaly adds /api/v1 to the URL.
app.include_router(health.router, prefix="/api/v1")

# Simple root endpoint just to test if the server is awake.
@app.get("/")
async def root():
    return {"message": "Welcome to the CASO-RAG API"}