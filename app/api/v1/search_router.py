from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.services.search_service import SearchService
from app.services.indexing_service import IndexingService
from app.schemas.search_response import SearchResultResponse
from app.schemas.event_payload import EventPayload
from app.models.entity_config import SearchEntityConfig

router = APIRouter()

@router.get("/search", response_model=List[SearchResultResponse])
def search(
    q: str = Query(..., min_length=2),
    company_id: int = Query(...),
    branch_ids: List[int] = Query(default=[]),
    db: Session = Depends(get_db)
):
    """Global search across all entities"""
    return SearchService.execute_search(db, q, company_id, branch_ids)


@router.get("/config")
def get_configs(db: Session = Depends(get_db)):
    """Get all entity route configurations"""
    configs = db.query(SearchEntityConfig).all()
    return [{"entity_type": c.entity_type, "base_url_route": c.base_url_route, "icon_name": c.icon_name} for c in configs]


@router.post("/config")
def create_config(
    entity_type: str,
    base_url_route: str,
    icon_name: str = None,
    db: Session = Depends(get_db)
):
    """Add new entity type configuration"""
    existing = db.query(SearchEntityConfig).filter(SearchEntityConfig.entity_type == entity_type).first()
    if existing:
        raise HTTPException(status_code=400, detail="Entity type already exists")
    
    config = SearchEntityConfig(entity_type=entity_type, base_url_route=base_url_route, icon_name=icon_name)
    db.add(config)
    db.commit()
    return {"message": f"Config for {entity_type} created", "entity_type": entity_type}


@router.post("/index")
def manual_index(payload: EventPayload, db: Session = Depends(get_db)):
    """Manually add/update an entity in the search index"""
    IndexingService.upsert_entity(db, payload)
    return {"message": f"Entity {payload.entity_type}:{payload.entity_id} indexed"}


@router.patch("/config/{entity_type}")
def update_config(
    entity_type: str,
    base_url_route: str = None,
    icon_name: str = None,
    db: Session = Depends(get_db)
):
    """Update entity type configuration"""
    config = db.query(SearchEntityConfig).filter(SearchEntityConfig.entity_type == entity_type).first()
    if not config:
        raise HTTPException(status_code=404, detail="Entity type not found")
    
    if base_url_route:
        config.base_url_route = base_url_route
    if icon_name:
        config.icon_name = icon_name
    
    db.commit()
    return {"message": f"Config for {entity_type} updated"}


@router.delete("/config/{entity_type}")
def delete_config(entity_type: str, db: Session = Depends(get_db)):
    """Remove entity type configuration"""
    config = db.query(SearchEntityConfig).filter(SearchEntityConfig.entity_type == entity_type).first()
    if not config:
        raise HTTPException(status_code=404, detail="Entity type not found")
    
    db.delete(config)
    db.commit()
    return {"message": f"Config for {entity_type} deleted"}


@router.delete("/index/{entity_type}/{entity_id}")
def delete_index(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    """Remove an entity from the search index"""
    IndexingService.delete_entity(db, entity_type, entity_id)
    return {"message": f"Entity {entity_type}:{entity_id} removed from index"}
