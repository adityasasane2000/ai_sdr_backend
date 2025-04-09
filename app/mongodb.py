import motor.motor_asyncio
from bson import ObjectId
from typing import List, Optional, Dict, Any
import os

# MongoDB connection string - replace with your actual connection string later
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority")
DATABASE_NAME = os.environ.get("MONGODB_DATABASE", "ai_sdr_platform")

# Create a client instance
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
users_collection = database.users
channels_collection = database.channels
prospects_collection = database.prospects

# Helper to convert MongoDB _id to string
def serialize_id(item):
    if item and "_id" in item:
        item["id"] = str(item["_id"])
        del item["_id"]
    return item

# User operations
async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return serialize_id(user)
    return None

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    user = await users_collection.find_one({"email": email})
    if user:
        return serialize_id(user)
    return None

async def get_users(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    users = []
    cursor = users_collection.find().skip(skip).limit(limit)
    async for user in cursor:
        users.append(serialize_id(user))
    return users

async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    user = await users_collection.insert_one(user_data)
    new_user = await users_collection.find_one({"_id": user.inserted_id})
    return serialize_id(new_user)

async def update_user(user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    
    await users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user_data}
    )
    
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    return serialize_id(updated_user)

async def delete_user(user_id: str) -> bool:
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

# Channel operations
async def get_channel(channel_id: str) -> Optional[Dict[str, Any]]:
    channel = await channels_collection.find_one({"_id": ObjectId(channel_id)})
    if channel:
        return serialize_id(channel)
    return None

async def get_channel_by_name(name: str) -> Optional[Dict[str, Any]]:
    channel = await channels_collection.find_one({"name": name})
    if channel:
        return serialize_id(channel)
    return None

async def get_channels(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    channels = []
    cursor = channels_collection.find().skip(skip).limit(limit)
    async for channel in cursor:
        channels.append(serialize_id(channel))
    return channels

async def create_channel(channel_data: Dict[str, Any]) -> Dict[str, Any]:
    channel = await channels_collection.insert_one(channel_data)
    new_channel = await channels_collection.find_one({"_id": channel.inserted_id})
    return serialize_id(new_channel)

async def update_channel(channel_id: str, channel_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    channel = await channels_collection.find_one({"_id": ObjectId(channel_id)})
    if not channel:
        return None
    
    await channels_collection.update_one(
        {"_id": ObjectId(channel_id)}, {"$set": channel_data}
    )
    
    updated_channel = await channels_collection.find_one({"_id": ObjectId(channel_id)})
    return serialize_id(updated_channel)

async def delete_channel(channel_id: str) -> bool:
    result = await channels_collection.delete_one({"_id": ObjectId(channel_id)})
    return result.deleted_count > 0

# Prospect operations
async def get_prospect(prospect_id: str) -> Optional[Dict[str, Any]]:
    prospect = await prospects_collection.find_one({"_id": ObjectId(prospect_id)})
    if prospect:
        return serialize_id(prospect)
    return None

async def get_prospects(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    prospects = []
    cursor = prospects_collection.find().skip(skip).limit(limit)
    async for prospect in cursor:
        prospects.append(serialize_id(prospect))
    return prospects

async def get_prospects_by_sdr(sdr_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    prospects = []
    cursor = prospects_collection.find({"sdr_id": sdr_id}).skip(skip).limit(limit)
    async for prospect in cursor:
        prospects.append(serialize_id(prospect))
    return prospects

async def create_prospect(prospect_data: Dict[str, Any]) -> Dict[str, Any]:
    prospect = await prospects_collection.insert_one(prospect_data)
    new_prospect = await prospects_collection.find_one({"_id": prospect.inserted_id})
    return serialize_id(new_prospect)

async def update_prospect(prospect_id: str, prospect_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    prospect = await prospects_collection.find_one({"_id": ObjectId(prospect_id)})
    if not prospect:
        return None
    
    await prospects_collection.update_one(
        {"_id": ObjectId(prospect_id)}, {"$set": prospect_data}
    )
    
    updated_prospect = await prospects_collection.find_one({"_id": ObjectId(prospect_id)})
    return serialize_id(updated_prospect)

async def delete_prospect(prospect_id: str) -> bool:
    result = await prospects_collection.delete_one({"_id": ObjectId(prospect_id)})
    return result.deleted_count > 0

async def search_prospects(query: str, sdr_id: Optional[str] = None) -> List[Dict[str, Any]]:
    search_query = {
        "$or": [
            {"company_name": {"$regex": query, "$options": "i"}},
            {"service_description": {"$regex": query, "$options": "i"}}
        ]
    }
    
    if sdr_id:
        search_query["sdr_id"] = sdr_id
    
    prospects = []
    cursor = prospects_collection.find(search_query)
    async for prospect in cursor:
        prospects.append(serialize_id(prospect))
    return prospects

# Channel assignment operations
async def assign_channel_to_sdr(sdr_id: str, channel_id: str) -> bool:
    # Update the user document to add the channel to their assigned channels
    result = await users_collection.update_one(
        {"_id": ObjectId(sdr_id)},
        {"$addToSet": {"assigned_channels": channel_id}}
    )
    return result.modified_count > 0

async def remove_channel_from_sdr(sdr_id: str, channel_id: str) -> bool:
    # Update the user document to remove the channel from their assigned channels
    result = await users_collection.update_one(
        {"_id": ObjectId(sdr_id)},
        {"$pull": {"assigned_channels": channel_id}}
    )
    return result.modified_count > 0

async def get_sdr_channels(sdr_id: str) -> List[Dict[str, Any]]:
    # Get the user document to find their assigned channels
    user = await users_collection.find_one({"_id": ObjectId(sdr_id)})
    if not user or "assigned_channels" not in user:
        return []
    
    # Get all the channels that match the IDs in the user's assigned_channels array
    channels = []
    cursor = channels_collection.find({"_id": {"$in": [ObjectId(ch_id) for ch_id in user["assigned_channels"]]}})
    async for channel in cursor:
        channels.append(serialize_id(channel))
    return channels
