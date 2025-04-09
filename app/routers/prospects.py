from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db
from ..auth import get_current_active_user, get_current_admin_user
from ..ai_search import search_prospects, SearchResult

router = APIRouter()

@router.get("/", response_model=List[schemas.Prospect])
def read_prospects(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # If admin, return all prospects, otherwise return only the SDR's prospects
    if current_user.is_admin:
        prospects = crud.get_prospects(db, skip=skip, limit=limit)
    else:
        prospects = crud.get_prospects_by_sdr(db, sdr_id=current_user.id, skip=skip, limit=limit)
    return prospects

@router.get("/{prospect_id}", response_model=schemas.Prospect)
def read_prospect(
    prospect_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_prospect = crud.get_prospect(db, prospect_id=prospect_id)
    if db_prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")

    # Check if the current user is an admin or the SDR who owns the prospect
    if not current_user.is_admin and db_prospect.sdr_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return db_prospect

@router.post("/", response_model=schemas.Prospect)
def create_prospect(
    prospect: schemas.ProspectCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Check if the channel exists and the SDR has access to it
    db_channel = crud.get_channel(db, channel_id=prospect.channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")

    if not current_user.is_admin:
        sdr_channels = crud.get_sdr_channels(db, sdr_id=current_user.id)
        if db_channel not in sdr_channels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SDR does not have access to this channel"
            )

    return crud.create_prospect(db=db, prospect=prospect, sdr_id=current_user.id)

@router.put("/{prospect_id}", response_model=schemas.Prospect)
def update_prospect(
    prospect_id: int, 
    prospect: schemas.ProspectUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_prospect = crud.get_prospect(db, prospect_id=prospect_id)
    if db_prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")

    # Check if the current user is an admin or the SDR who owns the prospect
    if not current_user.is_admin and db_prospect.sdr_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # If channel_id is being updated, check if the SDR has access to the new channel
    if prospect.channel_id is not None and prospect.channel_id != db_prospect.channel_id:
        db_channel = crud.get_channel(db, channel_id=prospect.channel_id)
        if db_channel is None:
            raise HTTPException(status_code=404, detail="Channel not found")

        if not current_user.is_admin:
            sdr_channels = crud.get_sdr_channels(db, sdr_id=current_user.id)
            if db_channel not in sdr_channels:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="SDR does not have access to this channel"
                )

    return crud.update_prospect(db, prospect_id=prospect_id, prospect=prospect)

@router.delete("/{prospect_id}", response_model=schemas.Prospect)
def delete_prospect(
    prospect_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_prospect = crud.get_prospect(db, prospect_id=prospect_id)
    if db_prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")

    # Check if the current user is an admin or the SDR who owns the prospect
    if not current_user.is_admin and db_prospect.sdr_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return crud.delete_prospect(db, prospect_id=prospect_id)

@router.get("/search/{query}", response_model=List[schemas.Prospect])
def search_prospects_db(
    query: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # This is a placeholder for the actual search functionality
    # In a real implementation, you would integrate with external APIs or services
    # to search for prospects based on the query

    # For now, we'll just return a filtered list of existing prospects
    if current_user.is_admin:
        prospects = db.query(models.Prospect).filter(
            models.Prospect.company_name.contains(query) | 
            models.Prospect.service_description.contains(query)
        ).all()
    else:
        prospects = db.query(models.Prospect).filter(
            models.Prospect.sdr_id == current_user.id,
            models.Prospect.company_name.contains(query) | 
            models.Prospect.service_description.contains(query)
        ).all()

    return prospects

@router.get("/ai-search/{channel_id}/{query}", response_model=List[SearchResult])
async def ai_search_prospects(
    channel_id: int,
    query: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Search for prospects using AI based on the query and channel.
    This endpoint uses an LLM to generate potential prospects."""
    # Check if the channel exists and the SDR has access to it
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if not current_user.is_admin:
        sdr_channels = crud.get_sdr_channels(db, sdr_id=current_user.id)
        if db_channel not in sdr_channels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SDR does not have access to this channel"
            )
    
    # Perform AI-powered search
    results = search_prospects(query, db_channel.name, channel_id)
    # print(f"Search results for {db_channel.name}: ", results)   
    
    return results