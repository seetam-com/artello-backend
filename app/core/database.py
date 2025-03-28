from motor.motor_asyncio import AsyncIOMotorClient
from neo4j import AsyncGraphDatabase
from app.core.config import settings

# MongoDB Connection
class MongoDB:
    client: AsyncIOMotorClient = None

    @classmethod
    def connect(cls):
        """Initialize MongoDB connection"""
        cls.client = AsyncIOMotorClient(settings.MONGO_URI)

    @classmethod
    def get_db(cls):
        """Return MongoDB Database instance"""
        return cls.client.get_database()

# Neo4j Connection
class Neo4jDB:
    driver = None

    @classmethod
    def connect(cls):
        """Initialize Neo4j connection"""
        cls.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    @classmethod
    def close(cls):
        """Close Neo4j connection"""
        if cls.driver:
            cls.driver.close()

# Initialize Databases
MongoDB.connect()
Neo4jDB.connect()
