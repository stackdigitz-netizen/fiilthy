from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "ai_ceo")

# Lazy initialization - don't connect at startup
client = None
db = None

def get_db():
    """Get database connection, creating it if needed"""
    global client, db
    
    if db is not None:
        return db
    
    if not MONGO_URL:
        raise ValueError(f"ERROR: MONGO_URL not set! Current value: '{MONGO_URL}'")
    
    print(f"[DB] Connecting to MongoDB...")
    print(f"[DB] URL starts with: {MONGO_URL[:60]}...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print(f"[DB] Connected to database: {DB_NAME}")
    return db

# These will be initialized on first use
projects = None
outputs = None
logs = None

def init_collections():
    """Initialize MongoDB collections"""
    global projects, outputs, logs
    database = get_db()
    projects = database.projects
    outputs = database.outputs
    logs = database.logs
    return projects, outputs, logs
