from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.api.services.pg.search_service import SearchService
from app.api.services.pg.indexing_service import IndexingService
from app.api.services.pg.config_service import ConfigService
from app.api.schemas.search_response import SearchResultResponse
from app.api.schemas.sectioned_response import SectionedSearchResponse
from app.api.schemas.event_payload import EventPayload

router = APIRouter()

# ==================== SEARCH ====================
@router.get("/search", response_model=SectionedSearchResponse)
def search(
    q: str = Query(..., min_length=2),
    company_id: int = Query(...),
    branch_ids: List[int] = Query(default=[]),
    entity_types: Optional[List[str]] = Query(default=None), # New filter
    page: int = Query(1, ge=1),                             # New pagination
    page_size: int = Query(20, ge=1, le=100),               # New pagination
    db: Session = Depends(get_db)
):
    """Global search across all entities"""
    offset = (page - 1) * page_size
    return SearchService.execute_search(
        db, q, company_id, branch_ids, 
        entity_types=entity_types, 
        limit=page_size, 
        offset=offset
    )


# ==================== INDEXING ====================
@router.get("/index/{entity_type}", response_model=List[SearchResultResponse])
def list_indexed_data(
    entity_type: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all indexed data for a specific entity type (for testing)"""
    return SearchService.get_indexed_data_by_type(db, entity_type, limit, offset)


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

