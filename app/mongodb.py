"""MongoDB connection and configuration."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
import os

# MongoDB connection string
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "cognify_db")

# Global client and database instances
_client: Optional[MongoClient] = None
_database = None


def get_mongodb_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000
            )
            # Test connection
            _client.admin.command('ping')
            print(f"Connected to MongoDB at {MONGODB_URL}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    return _client


def get_database():
    """Get database instance."""
    global _database
    if _database is None:
        client = get_mongodb_client()
        _database = client[DATABASE_NAME]
    return _database


def close_connection():
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()
        _client = None
        print("MongoDB connection closed")


# Initialize on import
try:
    get_mongodb_client()
except Exception as e:
    print(f"Warning: MongoDB not available: {e}")

