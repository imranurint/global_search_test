from pydantic import BaseModel
from typing import Optional, List

class EventPayload(BaseModel):
    event_action: str  # CREATE, UPDATE, DELETE
    entity_type: str
    entity_id: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    status: Optional[str] = None
    company_id: Optional[int] = None
    allowed_branch_ids: Optional[List[int]] = None
    search_text: Optional[str] = None
