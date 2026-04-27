from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.search_index import GlobalSearchIndex
from app.models.entity_config import SearchEntityConfig
from app.api.schemas.search_response import SearchResultResponse

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
    def get_indexed_data_by_type(
        cls, db: Session, entity_type: str, limit: int, offset: int
    ) -> List[SearchResultResponse]:
        """Fetch raw indexed data without full-text searching (paging support)"""
        results = db.query(GlobalSearchIndex).filter(
            GlobalSearchIndex.entity_type == entity_type
        ).order_by(GlobalSearchIndex.updated_at.desc()).offset(offset).limit(limit).all()

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

    @classmethod
    def execute_search(
        cls, db: Session, q: str, company_id: int, branch_ids: List[int]
    ) -> List[SearchResultResponse]:
        # 1. Clean and format for prefix matching
        # If user types "Jo", we want it to match "John"
        # We join words with :* to enable prefix matching for each word
        search_terms = " & ".join([f"{word}:*" for word in q.strip().split() if word])

        # Senior Engineering approach: Rank-ordered results
        # We rank by the ts_rank to ensure Title matches appear before Subtitle/Content matches.
        rank = func.ts_rank(GlobalSearchIndex.search_vector, func.to_tsquery('english', search_terms)).label("rank")

        query = db.query(GlobalSearchIndex, rank).filter(
            GlobalSearchIndex.company_id == company_id,
            GlobalSearchIndex.search_vector.op("@@")(func.to_tsquery('english', search_terms))
        ).order_by(rank.desc())
        
        if branch_ids:
            query = query.filter(
                (GlobalSearchIndex.allowed_branch_ids.is_(None)) |
                (GlobalSearchIndex.allowed_branch_ids.overlap(branch_ids))
            )
            
        results = query.limit(15).all()
        
        output = []
        for r, score in results:
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
