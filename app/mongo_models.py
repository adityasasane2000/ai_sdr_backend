from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

# Custom ObjectId field for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Base model with ID field
class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

# User models
class UserModel(MongoBaseModel):
    email: EmailStr
    hashed_password: Optional[str] = None
    full_name: str
    is_admin: bool = False
    is_active: bool = True
    assigned_channels: List[PyObjectId] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class UserCreateModel(BaseModel):
    email: EmailStr
    password: Optional[str] = None
    full_name: str
    is_admin: bool = False

class UserUpdateModel(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    assigned_channels: Optional[List[str]] = None

# Channel models
class ChannelModel(MongoBaseModel):
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ChannelCreateModel(BaseModel):
    name: str
    description: Optional[str] = None

class ChannelUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Prospect models
class ProspectModel(MongoBaseModel):
    company_name: str
    service_description: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    status: str = "New"
    notes: Optional[str] = None
    source_link: Optional[str] = None
    sdr_id: PyObjectId
    channel_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ProspectCreateModel(BaseModel):
    company_name: str
    service_description: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    status: str = "New"
    notes: Optional[str] = None
    source_link: Optional[str] = None
    channel_id: str

class ProspectUpdateModel(BaseModel):
    company_name: Optional[str] = None
    service_description: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    source_link: Optional[str] = None
    channel_id: Optional[str] = None
