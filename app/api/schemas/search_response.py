from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SearchResultResponse(BaseModel):
    id: UUID
    entity_type: str
    entity_id: str
    title: str
    subtitle: Optional[str]
    status: Optional[str]
    routing_url: str
    icon_name: Optional[str]

    class Config:
        from_attributes = True
