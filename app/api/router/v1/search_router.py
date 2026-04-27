from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.api.services.search_service import SearchService
from app.api.services.indexing_service import IndexingService
from app.api.services.config_service import ConfigService
from app.api.schemas.search_response import SearchResultResponse
from app.api.schemas.event_payload import EventPayload

router = APIRouter()

# ==================== SEARCH ====================
@router.get("/search", response_model=List[SearchResultResponse])
def search(
    q: str = Query(..., min_length=2),
    company_id: int = Query(...),
    branch_ids: List[int] = Query(default=[]),
    db: Session = Depends(get_db)
):
    """Global search across all entities"""
    return SearchService.execute_search(db, q, company_id, branch_ids)


# ==================== INDEXING ====================
@router.post("/index", status_code=status.HTTP_201_CREATED)
def manual_index(payload: EventPayload, db: Session = Depends(get_db)):
    """Manually add/update an entity in the search index"""
    IndexingService.upsert_entity(db, payload)
    return {"message": f"Entity {payload.entity_type}:{payload.entity_id} indexed"}


@router.delete("/index/{entity_type}/{entity_id}")
def delete_index(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    """Remove an entity from the search index"""
    IndexingService.delete_entity(db, entity_type, entity_id)
    return {"message": f"Entity {entity_type}:{entity_id} removed from index"}


# ==================== CONFIGURATION ====================
@router.get("/config")
def list_configs(db: Session = Depends(get_db)):
    """Get all entity route configurations"""
    return ConfigService.get_all_configs(db)


@router.post("/config", status_code=status.HTTP_201_CREATED)
def create_config(
    entity_type: str,
    base_url_route: str,
    icon_name: str = None,
    db: Session = Depends(get_db)
):
    """Add new entity type configuration"""
    ConfigService.create_config(db, entity_type, base_url_route, icon_name)
    return {"message": f"Config for {entity_type} created"}


@router.patch("/config/{entity_type}")
def update_config(
    entity_type: str,
    base_url_route: str = None,
    icon_name: str = None,
    db: Session = Depends(get_db)
):
    """Update entity type configuration"""
    ConfigService.update_config(db, entity_type, base_url_route, icon_name)
    return {"message": f"Config for {entity_type} updated"}


@router.delete("/config/{entity_type}")
def delete_config(entity_type: str, db: Session = Depends(get_db)):
    """Remove entity type configuration"""
    ConfigService.delete_config(db, entity_type)
    return {"message": f"Config for {entity_type} deleted"}

