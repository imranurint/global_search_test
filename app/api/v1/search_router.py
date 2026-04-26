from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.services.search_service import SearchService
from app.schemas.search_response import SearchResultResponse

router = APIRouter()

@router.get("/search", response_model=List[SearchResultResponse])
def search(
    q: str = Query(..., min_length=2),
    company_id: int = Query(...),
    branch_ids: List[int] = Query(default=[]),
    db: Session = Depends(get_db)
):
    return SearchService.execute_search(db, q, company_id, branch_ids)
