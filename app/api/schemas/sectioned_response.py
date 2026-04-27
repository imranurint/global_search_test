from pydantic import BaseModel
from typing import List, Dict
from app.api.schemas.search_response import SearchResultResponse

class SectionedSearchResponse(BaseModel):
    total_count: int
    sections: Dict[str, List[SearchResultResponse]]
