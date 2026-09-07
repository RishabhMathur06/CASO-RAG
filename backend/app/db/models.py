# Imports dependencies.
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.postgres_client import Base

class DocumentRecord(Base):
    """
        SQLAlchemy ORM model representing the document's table in postgreSQL.
        We use this to track the status of uploaded files.
    """
    __tablename__ = "dcouments"

    # A unique UUID string for each document.
    id = Column(String, primary_key=True, index=True)

    # The original file name (e.g., "report.pdf").
    filename = Column(String, nullable=False)

    # Tracks the ingestion pipeline state: 'processing', 'completed' or 'failed'.
    status = Column(String, default="processing")

    # Automatically records the exact timestamp when the row is created.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # A flexible JSON column to store extra metadata (like author, file size, etc.)
    extra_metadata = Column(JSON, default={})