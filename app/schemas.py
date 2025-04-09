from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for Google OAuth

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

# Channel schemas
class ChannelBase(BaseModel):
    name: str
    description: Optional[str] = None

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ChannelInDB(ChannelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Channel(ChannelInDB):
    pass

# Prospect schemas
class ProspectBase(BaseModel):
    company_name: str
    service_description: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    status: str = "New"
    notes: Optional[str] = None
    source_link: Optional[str] = None

class ProspectCreate(ProspectBase):
    channel_id: int

class ProspectUpdate(BaseModel):
    company_name: Optional[str] = None
    service_description: Optional[str] = None
    contact_info: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    source_link: Optional[str] = None
    channel_id: Optional[int] = None

class ProspectInDB(ProspectBase):
    id: int
    sdr_id: int
    channel_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Prospect(ProspectInDB):
    pass

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    is_admin: Optional[bool] = None
