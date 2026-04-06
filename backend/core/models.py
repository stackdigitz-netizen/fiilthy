from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "ai_ceo")

if not MONGO_URL:
    print("ERROR: MONGO_URL environment variable is not set!")
    print("Set it in Render dashboard: Environment > Add MONGO_URL")
    raise ValueError("MONGO_URL environment variable is required")

print(f"Connecting to MongoDB: {MONGO_URL[:50]}...")  # Print first 50 chars for debugging

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

projects = db.projects
outputs = db.outputs
logs = db.logs
