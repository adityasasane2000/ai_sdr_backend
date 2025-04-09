from sqlalchemy.orm import Session
from . import models, schemas
from .utils import get_password_hash

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password) if user.password else None
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db.delete(db_user)
    db.commit()
    return db_user

# Channel CRUD operations
def get_channel(db: Session, channel_id: int):
    return db.query(models.Channel).filter(models.Channel.id == channel_id).first()

def get_channel_by_name(db: Session, name: str):
    return db.query(models.Channel).filter(models.Channel.name == name).first()

def get_channels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Channel).offset(skip).limit(limit).all()

def create_channel(db: Session, channel: schemas.ChannelCreate):
    db_channel = models.Channel(
        name=channel.name,
        description=channel.description
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

def update_channel(db: Session, channel_id: int, channel: schemas.ChannelUpdate):
    db_channel = get_channel(db, channel_id)
    if not db_channel:
        return None
    
    update_data = channel.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_channel, key, value)
    
    db.commit()
    db.refresh(db_channel)
    return db_channel

def delete_channel(db: Session, channel_id: int):
    db_channel = get_channel(db, channel_id)
    if not db_channel:
        return None
    
    db.delete(db_channel)
    db.commit()
    return db_channel

# Prospect CRUD operations
def get_prospect(db: Session, prospect_id: int):
    return db.query(models.Prospect).filter(models.Prospect.id == prospect_id).first()

def get_prospects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prospect).offset(skip).limit(limit).all()

def get_prospects_by_sdr(db: Session, sdr_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Prospect).filter(models.Prospect.sdr_id == sdr_id).offset(skip).limit(limit).all()

def create_prospect(db: Session, prospect: schemas.ProspectCreate, sdr_id: int):
    db_prospect = models.Prospect(
        company_name=prospect.company_name,
        service_description=prospect.service_description,
        contact_info=prospect.contact_info,
        website=prospect.website,
        status=prospect.status,
        notes=prospect.notes,
        source_link=prospect.source_link,
        sdr_id=sdr_id,
        channel_id=prospect.channel_id
    )
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

def update_prospect(db: Session, prospect_id: int, prospect: schemas.ProspectUpdate):
    db_prospect = get_prospect(db, prospect_id)
    if not db_prospect:
        return None
    
    update_data = prospect.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prospect, key, value)
    
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

def delete_prospect(db: Session, prospect_id: int):
    db_prospect = get_prospect(db, prospect_id)
    if not db_prospect:
        return None
    
    db.delete(db_prospect)
    db.commit()
    return db_prospect

# Channel assignment operations
def assign_channel_to_sdr(db: Session, sdr_id: int, channel_id: int):
    db_sdr = get_user(db, sdr_id)
    db_channel = get_channel(db, channel_id)
    
    if not db_sdr or not db_channel:
        return None
    
    db_sdr.channels.append(db_channel)
    db.commit()
    return db_sdr

def remove_channel_from_sdr(db: Session, sdr_id: int, channel_id: int):
    db_sdr = get_user(db, sdr_id)
    db_channel = get_channel(db, channel_id)
    
    if not db_sdr or not db_channel:
        return None
    
    db_sdr.channels.remove(db_channel)
    db.commit()
    return db_sdr

def get_sdr_channels(db: Session, sdr_id: int):
    db_sdr = get_user(db, sdr_id)
    if not db_sdr:
        return None
    
    return db_sdr.channels
