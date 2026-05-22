from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .config import settings

MONGO_URI = getattr(settings, "mongodb_uri", "mongodb://localhost:27017")
DB_NAME = getattr(settings, "mongodb_db_name", "utilization_review_db")


class MongoDBManager:
    def __init__(self) -> None:
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None

    def connect(self, uri: str, db_name: str) -> None:
        print(f"[Database] Connecting to MongoDB at: {uri}")
        self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        self.db = self.client[db_name]
        print(f"[Database] Successfully bound to database: {db_name}")
        
        try:
            self.client.admin.command('ping')
            print(f"[Database] Successfully bound to database storage context: {db_name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as ce:
            print("\n" + "="*60)
            print("[DATABASE CRITICAL ERROR] BOOTSTRAP FAILED!")
            print(f"Unable to establish immediate connection to MongoDB instance.")
            print(f"Technical Details: {str(ce)}")
            print("="*60 + "\n")
            
            raise SystemExit("[Runtime Aborted] Backend safely terminated due to missing database infrastructure.")

    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            print("[Database] connection successfully disconnect.")
            # Reset state variables
            self.client = None
            self.db = None

    def get_collection(self, collection_name: str = "revisions"):
        if self.db is None:
            raise RuntimeError("[Database Error] Attempted to query prior to database initialization.")
        return self.db[collection_name]


db_manager = MongoDBManager()


def connect_to_mongo() -> None:
    db_manager.connect(uri=MONGO_URI, db_name=DB_NAME)


def close_mongo_connection() -> None:
    db_manager.disconnect()


def get_revisions_collection():
    return db_manager.get_collection("revisions")
