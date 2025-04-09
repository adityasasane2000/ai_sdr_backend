import asyncio
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from app.utils import get_password_hash

# MongoDB connection string - replace with your actual connection string later
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority")
DATABASE_NAME = os.environ.get("MONGODB_DATABASE", "ai_sdr_platform")

async def init_db():
    # Create a synchronous client for initialization
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Collections
    users_collection = db.users
    channels_collection = db.channels
    prospects_collection = db.prospects
    
    try:
        # Check if admin user exists
        admin = users_collection.find_one({"email": "admin@example.com"})
        if not admin:
            print("Creating admin user...")
            admin_id = users_collection.insert_one({
                "email": "admin@example.com",
                "hashed_password": get_password_hash("admin123"),
                "full_name": "Admin User",
                "is_admin": True,
                "is_active": True,
                "assigned_channels": [],
                "created_at": datetime.utcnow()
            }).inserted_id
            print(f"Admin user created with ID: {admin_id}")
        else:
            print("Admin user already exists")
            admin_id = admin["_id"]

        # Check if SDR user exists
        sdr = users_collection.find_one({"email": "sdr@example.com"})
        if not sdr:
            print("Creating SDR user...")
            sdr_id = users_collection.insert_one({
                "email": "sdr@example.com",
                "hashed_password": get_password_hash("sdr123"),
                "full_name": "SDR User",
                "is_admin": False,
                "is_active": True,
                "assigned_channels": [],
                "created_at": datetime.utcnow()
            }).inserted_id
            print(f"SDR user created with ID: {sdr_id}")
        else:
            print("SDR user already exists")
            sdr_id = sdr["_id"]

        # Create channels if they don't exist
        channels = ["Twitter", "LinkedIn", "Instagram", "Facebook", "Email"]
        channel_ids = []
        
        for channel_name in channels:
            channel = channels_collection.find_one({"name": channel_name})
            if not channel:
                print(f"Creating channel: {channel_name}")
                channel_id = channels_collection.insert_one({
                    "name": channel_name,
                    "description": f"{channel_name} prospecting channel",
                    "created_at": datetime.utcnow()
                }).inserted_id
                print(f"Channel created with ID: {channel_id}")
                channel_ids.append(channel_id)
            else:
                print(f"Channel {channel_name} already exists")
                channel_ids.append(channel["_id"])

        # Assign channels to SDR
        if sdr_id:
            print(f"Assigning channels to SDR")
            users_collection.update_one(
                {"_id": sdr_id},
                {"$set": {"assigned_channels": channel_ids}}
            )
            print("Channels assigned to SDR")

        print("Database initialized successfully")
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(init_db())
