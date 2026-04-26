from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.search_index import GlobalSearchIndex
from app.models.entity_config import SearchEntityConfig
from app.schemas.search_response import SearchResultResponse

class SearchService:
    _route_cache = {}

    @classmethod
    def _get_config(cls, db: Session, entity_type: str):
        if not cls._route_cache:
            configs = db.query(SearchEntityConfig).all()
            for c in configs:
                cls._route_cache[c.entity_type] = {
                    "route": c.base_url_route,
                    "icon": c.icon_name
                }
        return cls._route_cache.get(entity_type, {"route": "/fallback/{id}", "icon": "default"})

    @classmethod
    def execute_search(
        cls, db: Session, q: str, company_id: int, branch_ids: List[int]
    ) -> List[SearchResultResponse]:
        query = db.query(GlobalSearchIndex).filter(
            GlobalSearchIndex.company_id == company_id,
            GlobalSearchIndex.search_vector.op("@@")(func.to_tsquery('english', f'{q}:*'))
        )
        
        if branch_ids:
            query = query.filter(
                (GlobalSearchIndex.allowed_branch_ids.is_(None)) |
                (GlobalSearchIndex.allowed_branch_ids.overlap(branch_ids))
            )
            
        results = query.limit(15).all()
        
        output = []
        for r in results:
            cfg = cls._get_config(db, r.entity_type)
            output.append(SearchResultResponse(
                id=r.id,
                entity_type=r.entity_type,
                entity_id=r.entity_id,
                title=r.title,
                subtitle=r.subtitle,
                status=r.status,
                routing_url=cfg["route"].format(id=r.entity_id),
                icon_name=cfg["icon"]
            ))
        return output
