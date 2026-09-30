# Imports dependencies.
from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "casorag_neo4j_password"):
        # Connect to local Docker container running Neo4j
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._verify_connection()

    def _verify_connection(self):
        """
            Pings the database to ensure we successfully connected.
        """
        try:
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j Knowledge Graph.")
            
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")

    def close(self):
        # The connection needs to be manually close the connection
        # when app shuts down.
        self.driver.close()

# Creating Instance
neo4j_db = Neo4jClient()