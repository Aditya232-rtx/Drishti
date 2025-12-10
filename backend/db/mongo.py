"""MongoDB connection and database access."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from backend.config.settings import get_settings


class MongoDB:
    """MongoDB connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        settings = get_settings()
        cls.client = AsyncIOMotorClient(settings.MONGO_URI)
        cls.db = cls.client[settings.MONGO_DB_NAME]
        
        # Test connection
        await cls.client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls.client:
            cls.client.close()
            print("❌ Disconnected from MongoDB")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.db
    
    @classmethod
    def get_collection(cls, name: str):
        """Get collection by name."""
        return cls.get_database()[name]


# Collection accessors
def get_users_collection():
    """Get users collection."""
    return MongoDB.get_collection("users")


def get_sessions_collection():
    """Get sessions collection."""
    return MongoDB.get_collection("sessions")


def get_messages_collection():
    """Get messages collection."""
    return MongoDB.get_collection("messages")


def get_documents_collection():
    """Get documents collection."""
    return MongoDB.get_collection("documents")


def get_chunks_collection():
    """Get chunks collection."""
    return MongoDB.get_collection("chunks")
