# Imports dependencies
from neo4j import AsyncGraphDatabase
from app.config import get_settings

settings = get_settings()

class Neo4jConnection:
    """
        Manages relationship with the Neo4j database.
    """
    def __init__(self):
        self.driver = None

    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        await self.driver.verify_connectivity()
        print("Connected to Neo4j successfully.")

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def init_constraints(self):
        """
            Initializes graph schema constraints to ensure uniqueness
            and fast lookups.
        """
        # CONSTRAINTS: Rule that checks if the new chunk, doc, entity already exists and if not create one.
        # ENTITY: Maps each chunk to it's doc and each entity name with it's type.
        queries = [
            "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;",
            "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;",
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;",
            "CREATE INDEX chunk_doc_idx IF NOT EXISTS FOR (c:Chunk) ON (c.document_id);",
            "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.name, e.type);"
        ]

        # Opens a session and loops through each rule within the queries.
        async with self.driver.session() as session:
            for query in queries:
                await session.run(query)

        print("Neo4j constraints and indices initialized.")

neo4j_db = Neo4jConnection()