from pydantic import BaseModel
from typing import Optional, Union
from uuid import UUID

class SearchResultResponse(BaseModel):
    # Change from UUID to str to support Elasticsearch IDs
    id: Union[str, UUID] 
    entity_type: str
    entity_id: str
    title: str
    subtitle: Optional[str]
    status: Optional[str]
    routing_url: str
    icon_name: Optional[str]

    class Config:
        from_attributes = True
