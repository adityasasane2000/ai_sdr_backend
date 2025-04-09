from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db
from ..auth import get_current_admin_user, get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Channel])
def read_channels(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    channels = crud.get_channels(db, skip=skip, limit=limit)
    return channels

@router.get("/{channel_id}", response_model=schemas.Channel)
def read_channel(
    channel_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel

@router.post("/", response_model=schemas.Channel)
def create_channel(
    channel: schemas.ChannelCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_channel = crud.get_channel_by_name(db, name=channel.name)
    if db_channel:
        raise HTTPException(status_code=400, detail="Channel already exists")
    return crud.create_channel(db=db, channel=channel)

@router.put("/{channel_id}", response_model=schemas.Channel)
def update_channel(
    channel_id: int, 
    channel: schemas.ChannelUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_channel = crud.update_channel(db, channel_id=channel_id, channel=channel)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel

@router.delete("/{channel_id}", response_model=schemas.Channel)
def delete_channel(
    channel_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_channel = crud.delete_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel

@router.post("/{channel_id}/assign/{sdr_id}", response_model=schemas.User)
def assign_channel_to_sdr(
    channel_id: int,
    sdr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_sdr = crud.assign_channel_to_sdr(db, sdr_id=sdr_id, channel_id=channel_id)
    if db_sdr is None:
        raise HTTPException(status_code=404, detail="User or channel not found")
    return db_sdr

@router.delete("/{channel_id}/assign/{sdr_id}", response_model=schemas.User)
def remove_channel_from_sdr(
    channel_id: int,
    sdr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_sdr = crud.remove_channel_from_sdr(db, sdr_id=sdr_id, channel_id=channel_id)
    if db_sdr is None:
        raise HTTPException(status_code=404, detail="User or channel not found")
    return db_sdr

@router.get("/sdr/{sdr_id}", response_model=List[schemas.Channel])
def read_sdr_channels(
    sdr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Check if the current user is an admin or the SDR in question
    if not current_user.is_admin and current_user.id != sdr_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    channels = crud.get_sdr_channels(db, sdr_id=sdr_id)
    if channels is None:
        raise HTTPException(status_code=404, detail="SDR not found")
    return channels