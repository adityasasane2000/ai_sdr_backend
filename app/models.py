from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

# Association table for SDR-Channel many-to-many relationship
sdr_channel = Table(
    "sdr_channel",
    Base.metadata,
    Column("sdr_id", Integer, ForeignKey("users.id")),
    Column("channel_id", Integer, ForeignKey("channels.id")),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # Nullable for Google OAuth users
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    prospects = relationship("Prospect", back_populates="sdr")
    channels = relationship("Channel", secondary=sdr_channel, back_populates="sdrs")

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sdrs = relationship("User", secondary=sdr_channel, back_populates="channels")
    prospects = relationship("Prospect", back_populates="channel")

class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    service_description = Column(Text, nullable=True)
    contact_info = Column(String, nullable=True)
    website = Column(String, nullable=True)
    status = Column(String, default="New")  # New, Contacted, Qualified, Disqualified, etc.
    notes = Column(Text, nullable=True)
    source_link = Column(String, nullable=True)  # Added source link field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    sdr_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    
    # Relationships
    sdr = relationship("User", back_populates="prospects")
    channel = relationship("Channel", back_populates="prospects")
