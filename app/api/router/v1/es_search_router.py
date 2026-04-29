from fastapi import APIRouter, Query, status
from typing import List, Optional
# Import your new Elastic Services
from app.api.services.es.elastic_search_service import ElasticSearchService
from app.api.services.es.elastic_indexing_service import ElasticIndexingService
from app.api.services.es.elastic_config_service import ConfigService

from app.api.schemas.search_response import SearchResultResponse
from app.api.schemas.sectioned_response import SectionedSearchResponse
from app.api.schemas.event_payload import EventPayload

router = APIRouter()

# ==================== SEARCH (Elasticsearch Powered) ====================
@router.get("/es/search", response_model=SectionedSearchResponse)
def search(
    q: str = Query(..., min_length=2),
    company_id: int = Query(...),
    branch_ids: Optional[List[int]] = Query(default=None)
):
    """Global fuzzy search across 3M+ entities in Elasticsearch"""
    # Notice: No 'db' dependency here anymore!
    return ElasticSearchService.execute_search(q, company_id, branch_ids)


# ==================== INDEXING (Elasticsearch Powered) ====================
@router.get("/index/{entity_type}", response_model=List[SearchResultResponse])
def list_indexed_data(
    entity_type: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Fetch raw indexed data directly from ES"""
    return ElasticSearchService.get_data_by_type(entity_type, limit, offset)


@router.post("/index", status_code=status.HTTP_201_CREATED)
def manual_index(payload: EventPayload):
    """Manually add/update an entity in the Elasticsearch index"""
    ElasticIndexingService.upsert_entity(payload)
    return {"message": f"Entity {payload.entity_type}:{payload.entity_id} synced to ES"}


@router.delete("/index/{entity_type}/{entity_id}")
def delete_index(entity_type: str, entity_id: str):
    """Remove an entity from the Elasticsearch index"""
    ElasticIndexingService.delete_entity(entity_type, entity_id)
    return {"message": f"Entity {entity_type}:{entity_id} removed from ES"}


# ==================== CONFIGURATION (Elasticsearch Powered) ====================
@router.get("/config")
def list_configs():
    """Get all entity route configurations from ES"""
    return ConfigService.get_all_configs()


@router.post("/config", status_code=status.HTTP_201_CREATED)
def create_config(
    entity_type: str,
    base_url_route: str,
    icon_name: str = None
):
    """Add new entity type configuration to ES index"""
    ConfigService.create_config(entity_type, base_url_route, icon_name)
    return {"message": f"Config for {entity_type} saved to ES"}


@router.delete("/config/{entity_type}")
def delete_config(entity_type: str):
    """Remove entity configuration from ES"""
    ConfigService.delete_config(entity_type)
    return {"message": f"Config for {entity_type} deleted"}