# Imports dependencies.
# SQLAlchemy: ORM which translates Python code into SQL code and manages connection to PostgresSQL.
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import get_settings

settings = get_settings()

# Initializes connection with Postgres DB.
engine = create_async_engine(settings.database_url, echo=False)

# Creates new "Sessions" with the db.
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# When user makes API request, FastAPI calls this.
async def get_db_session(): 
    async with AsyncSessionLocal() as session: # Returns a new db session.
        yield session   # Hands API route the current session.